import os
from cs50 import SQL

if not os.path.exists("instance"):
    os.makedirs("instance")
if not os.path.exists("instance/database.db"):
    open("instance/database.db", "a").close()

db = SQL("sqlite:///instance/database.db")

def create_tables():
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'admin'))
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            instructions TEXT,
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            active INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            is_mcq INTEGER NOT NULL CHECK (is_mcq IN (0, 1)),
            correct_answer TEXT,
            marks INTEGER DEFAULT 1,
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            is_correct INTEGER DEFAULT 0,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            mcq_score REAL DEFAULT 0,
            subjective_score REAL DEFAULT 0,
            total_score REAL DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (exam_id) REFERENCES exams(id)
        );
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer_text TEXT NOT NULL,
            reference_text TEXT,
            score REAL DEFAULT 0,
            FOREIGN KEY (submission_id) REFERENCES submissions(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        );
    """)

create_tables()
