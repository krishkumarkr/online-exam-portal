
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5)])
    confirm = PasswordField("Confirm Password", validators=[EqualTo('password', message="Passwords do not match.")])
    role = SelectField("Role", choices=[('student', 'Student'), ('teacher', 'Teacher')])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CreateExamForm(FlaskForm):
    title = StringField("Exam Title", validators=[DataRequired()])
    instructions = StringField("Instructions", validators=[DataRequired()])
    submit = SubmitField("Create Exam")

class ProfileForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Update Profile")

class AddQuestionForm(FlaskForm):
    question_text = TextAreaField("Question", validators=[DataRequired()])
    is_mcq = SelectField("Type", choices=[('1', 'MCQ'), ('0', 'Subjective')], validators=[DataRequired()])
    correct_answer = StringField("Correct Answer", validators=[DataRequired()])
    marks = StringField("Marks", validators=[DataRequired()])

    # MCQ Options
    option_a = StringField("Option A")
    option_b = StringField("Option B")
    option_c = StringField("Option C")
    option_d = StringField("Option D")

    submit = SubmitField("Add Question")


