# app/routes/auth.py
from flask import Blueprint, render_template, redirect, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegisterForm
from app.models import db

auth = Blueprint('auth', __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        role = form.role.data

        user_email = db.execute("SELECT * FROM users WHERE email = :email",
                          email=email)
        user_username = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        if user_email:
            flash("Email already registered!", "danger")
            return render_template("auth/register.html", form=form)
        
        if user_username:
            flash("Username already registered!", "danger")
            return render_template("auth/register.html", form=form)
            
        db.execute("INSERT INTO users (username, email, password, role) VALUES (:u, :e, :p, :r)",
                   u=username, e=email, p=password, r=role)
        flash("Account created! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.execute("SELECT * FROM users WHERE email = :email", email=email)

        if not user:
            flash("User not found! Please register first", "danger")
            return render_template("auth/login.html", form=form)
        
        if not check_password_hash(user[0]["password"], password):
            flash("Incorrect password!", "danger")
            return render_template("auth/login.html", form=form)
        
        
        session["user_id"] = user[0]["id"]
        session["username"] = user[0]["username"]
        session["role"] = user[0]["role"]
        flash("Welcome, " + user[0]["username"], "success")

        if user[0]["role"] == "student":
            return redirect(url_for("student.dashboard"))
        elif user[0]["role"] == "teacher":
            return redirect(url_for("teacher.dashboard"))
        else:
            return redirect(url_for("admin.dashboard"))

    return render_template("auth/login.html", form=form)

@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
