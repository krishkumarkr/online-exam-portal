
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
# from app.forms import CreateExamForm, AddQuestionForm
from app.models import db
from functools import wraps
import datetime

teacher = Blueprint("teacher", __name__)

# Role check decorator
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "teacher":
            flash("Access denied. Teachers only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# 1. Teacher Dashboard
@teacher.route("/teacher/dashboard")
@teacher_required
def dashboard():
    exams = db.execute( "SELECT * FROM exams WHERE created_by = :uid ORDER BY created_at DESC",uid=session["user_id"])
    return render_template("teacher/dashboard.html", exams=exams)

# 2. Create New Exam
from app.forms import CreateExamForm  # Import your WTForm

@teacher.route("/teacher/create_exam", methods=["GET", "POST"])
@teacher_required
def create_exam():
    form = CreateExamForm()
    if form.validate_on_submit():
        title = form.title.data
        instructions = form.instructions.data
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.execute("""
            INSERT INTO exams (title, instructions, created_by, created_at, active)
            VALUES (:t, :i, :uid, :c, 0)
        """, t=title, i=instructions, uid=session["user_id"], c=created_at)

        flash("Exam created. Now add questions.", "success")
        return redirect(url_for("teacher.manage_exams"))

    return render_template("teacher/create_exam.html", form=form)


# add questions
from app.forms import AddQuestionForm

@teacher.route("/teacher/exam/<int:exam_id>/add_question", methods=["GET", "POST"])
@teacher_required
def add_question(exam_id):
    form = AddQuestionForm()
    if form.validate_on_submit():
        question_text = form.question_text.data
        is_mcq = int(form.is_mcq.data)
        correct_answer = form.correct_answer.data
        marks = int(form.marks.data)

        db.execute("""
            INSERT INTO questions (exam_id, question_text, is_mcq, correct_answer, marks)
            VALUES (:eid, :qt, :mcq, :ca, :m)
        """, eid=exam_id, qt=question_text, mcq=is_mcq, ca=correct_answer, m=marks)

        question_id = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]

        if is_mcq:
            options = [
                ('A', form.option_a.data),
                ('B', form.option_b.data),
                ('C', form.option_c.data),
                ('D', form.option_d.data),
            ]
            for label, text in options:
                if text:
                    is_correct = 1 if correct_answer.strip().lower() == label.lower() else 0
                    db.execute("""
                        INSERT INTO options (question_id, option_text, is_correct)
                        VALUES (:qid, :text, :isc)
                    """, qid=question_id, text=text, isc=is_correct)

        flash("Question added successfully!", "success")
        return redirect(url_for('teacher.add_question', exam_id=exam_id))

    return render_template("teacher/add_question.html", form=form, exam_id=exam_id)



# 3. Manage Exams
@teacher.route("/teacher/exams")
@teacher_required
def manage_exams():
    exams = db.execute("SELECT * FROM exams WHERE created_by = :uid", uid=session["user_id"])
    return render_template("teacher/manage_exams.html", exams=exams)

#soft show/hide exam option for teacher
@teacher.route("/teacher/exam/<int:exam_id>/toggle", methods=["POST"])
@teacher_required
def toggle_exam_status(exam_id):
    exam = db.execute("SELECT * FROM exams WHERE id = :id AND created_by = :uid", id=exam_id, uid=session["user_id"])
    if not exam:
        flash("Exam not found or unauthorized access.", "danger")
        return redirect(url_for("teacher.manage_exams"))

    current_status = exam[0]["active"]
    db.execute("UPDATE exams SET active = :new_status WHERE id = :id", new_status=0 if current_status else 1, id=exam_id)

    flash("Exam status updated!", "success")
    return redirect(url_for("teacher.manage_exams"))

#for previewing the image
@teacher.route("/teacher/exam/<int:exam_id>/preview")
@teacher_required
def preview_exam(exam_id):
    exam = db.execute("SELECT * FROM exams WHERE id = :id", id=exam_id)
    if not exam:
        flash("Exam not found.", "danger")
        return redirect(url_for("teacher.manage_exams"))

    questions = db.execute("SELECT * FROM questions WHERE exam_id = :eid", eid=exam_id)

    options_map = {}
    for q in questions:
        if q["is_mcq"]:
            opts = db.execute("SELECT * FROM options WHERE question_id = :qid", qid=q["id"])
            options_map[q["id"]] = opts

    return render_template("teacher/preview_exam.html", exam=exam[0], questions=questions, options_map=options_map)

#edit exam
@teacher.route("/teacher/exam/<int:exam_id>/edit", methods=["GET", "POST"])
@teacher_required
def edit_exam(exam_id):
    exam = db.execute("SELECT * FROM exams WHERE id = :id AND created_by = :uid", id=exam_id, uid=session["user_id"])
    if not exam:
        flash("Exam not found.", "danger")
        return redirect(url_for("teacher.manage_exams"))

    exam = exam[0]
    form = CreateExamForm(
        title=exam["title"],
        instructions=exam["instructions"]
    )

    if form.validate_on_submit():
        db.execute("""
            UPDATE exams SET title = :t, instructions = :i WHERE id = :id
        """, t=form.title.data, i=form.instructions.data, id=exam_id)

        flash("Exam updated successfully!", "success")
        return redirect(url_for("teacher.manage_exams"))

    return render_template("teacher/edit_exam.html", form=form)


#delete exam
@teacher.route("/teacher/exam/<int:exam_id>/delete", methods=["POST"])
@teacher_required
def delete_exam(exam_id):
    # Delete all options related to questions in this exam
    question_ids = db.execute("SELECT id FROM questions WHERE exam_id = :eid", eid=exam_id)
    for q in question_ids:
        db.execute("DELETE FROM options WHERE question_id = :qid", qid=q["id"])

    # Delete questions, then the exam
    db.execute("DELETE FROM questions WHERE exam_id = :eid", eid=exam_id)
    db.execute("DELETE FROM exams WHERE id = :eid AND created_by = :uid", eid=exam_id, uid=session["user_id"])

    flash("Exam and its questions deleted successfully.", "success")
    return redirect(url_for("teacher.manage_exams"))




# 4. View Submissions for Exam
@teacher.route("/teacher/exam/<int:exam_id>/submissions")
@teacher_required
def view_submissions(exam_id):
    submissions = db.execute("""
        SELECT s.id, u.username, s.timestamp, s.mcq_score, s.subjective_score, s.total_score
        FROM submissions s
        JOIN users u ON s.student_id = u.id
        WHERE s.exam_id = :eid
    """, eid=exam_id)
    return render_template("teacher/submissions.html", submissions=submissions)

# 5. Trigger AI Evaluation (optional)
@teacher.route("/teacher/submission/<int:sub_id>/evaluate")
@teacher_required
def evaluate_submission(sub_id):
    # Fetch student's answers and reference
    submission = db.execute("SELECT * FROM answers WHERE submission_id = :sid", sid=sub_id)
    for ans in submission:
        # Write student's answer and reference answer to files
        with open("cpp_ai/input.txt", "w") as f: f.write(ans["answer_text"])
        with open("cpp_ai/reference.txt", "w") as f: f.write(ans["reference_text"])

        import subprocess
        result = subprocess.check_output(["./cpp_ai/plagiarism"]).decode("utf-8").strip()
        similarity = float(result)  # assuming it returns a float
        db.execute("UPDATE answers SET score = :s WHERE id = :aid", s=similarity * 10, aid=ans["id"])

    flash("AI evaluation completed.", "success")
    return redirect(url_for("teacher.dashboard"))

# 6. View Results
@teacher.route("/teacher/results")
@teacher_required
def view_results():
    results = db.execute("""
        SELECT e.title, u.username, s.total_score
        FROM submissions s
        JOIN users u ON s.student_id = u.id
        JOIN exams e ON s.exam_id = e.id
        WHERE e.created_by = :uid
    """, uid=session["user_id"])
    return render_template("teacher/results.html", results=results)

# 7. Profile Settings
from app.forms import ProfileForm  # import the form

@teacher.route("/teacher/profile", methods=["GET", "POST"])
@teacher_required
def profile():
    user = db.execute("SELECT * FROM users WHERE id = :uid", uid=session["user_id"])[0]
    form = ProfileForm()

    if form.validate_on_submit():
        new_email = form.email.data
        new_password = form.password.data
        db.execute("UPDATE users SET email = :e, password = :p WHERE id = :uid",
                   e=new_email, p=new_password, uid=session["user_id"])
        flash("Profile updated!", "success")
        return redirect(url_for("teacher.profile"))  # Optional redirect to clear form

    # Pre-fill form with current user data (only on GET)
    if request.method == "GET":
        form.email.data = user["email"]

    return render_template("teacher/profile.html", form=form, user=user)
