import os
import shutil
from flask import Blueprint
from flask import request, redirect, url_for, render_template, session
from models import User, db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from extensions import mail
import random

auth = Blueprint("auth", __name__)

@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("files.dashboard"))

        return "<h1>Invalid username or password</h1>"

    return render_template("login.html")



@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")



        username = username.strip()

        if not username:
            return "<h1>Username cannot be empty</h1>"

        if len(username) > 50:
            return "<h1>Username too long</h1>"

        if len(password) < 6:
            return "<h1>Password must be at least 6 characters</h1>"



        if User.query.count() >= 11:
            return "<h1>Maximum users reached</h1>"

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "<h1>Username already exists</h1>"


        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            return "<h1>Email already exists</h1>"





        verification_code = str(random.randint(100000, 999999))

        session["verification_code"] = verification_code
        session["pending_username"] = username
        session["pending_email"] = email
        session["pending_password"] = password

        msg = Message(
            subject="Cloud Storage Verification Code",
            sender="akt.cloud.storage@gmail.com",
            recipients=[email]
        )

        msg.body = f"Your verification code is: {verification_code}"

        mail.send(msg)
        return redirect(url_for("auth.verify_email"))


        os.makedirs(
            os.path.join("uploads", username),
            exist_ok=True
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html")



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))




@auth.route("/delete-account", methods=["GET", "POST"])
@login_required
def delete_account():

    if request.method == "POST":

        password = request.form.get("password")

        if not check_password_hash(
            current_user.password,
            password
        ):
            return """
            <h1>Wrong password</h1>
            <a href="/delete-account">Try Again</a>
            """

        username = current_user.username

        user_folder = os.path.join(
            "uploads",
            username
        )

        logout_user()

        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)

        user = User.query.filter_by(
            username=username
        ).first()

        if user:
            db.session.delete(user)
            db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("delete_account.html")
   


@auth.route("/test-email")
def test_email():
    msg = Message(
        subject="Cloud Storage Test",
        sender="akt.cloud.storage@gmail.com",
        recipients=["akt629201@gmail.com"]
    )

    msg.body = "If you received this email, Flask-Mail is working!"

    mail.send(msg)

    return "Email sent!"


@auth.route("/verify-email", methods=["GET", "POST"])
def verify_email():

    if request.method == "POST":

        entered_code = request.form.get("code")

        if entered_code == session.get("verification_code"):
            user = User(
                username=session["pending_username"],
                email=session["pending_email"],
                password=generate_password_hash(
                    session["pending_password"]
                )
            )

            db.session.add(user)
            db.session.commit()

            session.pop("verification_code", None)
            session.pop("pending_username", None)
            session.pop("pending_email", None)
            session.pop("pending_password", None)


            return "Account Created Successfully"
        
        return "Invalid Verification Code"

    return render_template("verify_email.html")
