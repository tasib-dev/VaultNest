import secrets
import shutil
MAX_STORAGE = 2 * 1024 * 1024 * 1024
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024
app.config["SECRET_KEY"] = "fhdjugirjghi76786598645uyh8itrjbut9t8r7y8jsduhriutyghue"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cloud.db"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)



class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)

    username = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




def get_folder_size(folder):

    total_size = 0

    for dirpath, dirnames, filenames in os.walk(folder):

        for filename in filenames:

            file_path = os.path.join(
                dirpath,
                filename
            )

            total_size += os.path.getsize(file_path)

    return total_size







@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        return "<h1>Invalid username or password</h1>"

    return """
    <h1>Cloud Drive Login</h1>

    <form method="POST">
        Username:
        <input type="text" name="username">

        <br><br>

        Password:
        <input type="password" name="password">

        <br><br>

        <button type="submit">
            Login
        </button>

        <br><br>
        <a href="/register">Register</a>

    </form>
    """


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")



        username = username.strip()

        if not username:
            return "<h1>Username cannot be empty</h1>"

        if len(username) > 50:
            return "<h1>Username too long</h1>"

        if len(password) < 6:
            return "<h1>Password must be at least 6 characters</h1>"



        if User.query.count() >= 10:
            return "<h1>Maximum users reached</h1>"

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "<h1>Username already exists</h1>"

        user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        os.makedirs(
            os.path.join("uploads", username),
            exist_ok=True
        )

        return redirect(url_for("login"))

    return """
    <h1>Register</h1>

    <form method="POST">

        Username:
        <input type="text" name="username">

        <br><br>

        Password:
        <input type="password" name="password">

        <br><br>

        <button type="submit">
            Register
        </button>

    </form>
    """






@app.route("/dashboard")
@login_required
def dashboard():

    user_folder = os.path.join(
        "uploads",
        current_user.username
    )

    os.makedirs(user_folder, exist_ok=True)

    files = os.listdir(user_folder)
    used_bytes = get_folder_size(user_folder)

    used_mb = round(
        used_bytes / (1024 * 1024),
        2
    )

    max_gb = round(
            MAX_STORAGE / (1024 * 1024 * 1024),
            2
            )

    file_list = ""

    for file in files:
        shared = SharedFile.query.filter_by(
            username=current_user.username,
            filename=file
        ).first()

        if shared:
            action = f'<a href="/unshare/{file}">Stop Sharing</a>'
        else:
            action = f'<a href="/share/{file}">Share</a>'
        

        file_list += (
            f'<li>'
            f'<a href="/download/{file}">{file}</a>'
            f' | '
            f'{action}'
            f' | '
            f'<a href="/delete/{file}">Delete</a>'
            f'</li>'
        )   

    return f"""
    <h1>Dashboard</h1>

    <p>Logged in as: {current_user.username}</p>

    <p>Storage Used: {used_mb} MB / {max_gb} GB</p>

    <h2>Your Files</h2>

    <ul>
        {file_list}
    </ul>

    <a href="/upload">Upload File</a>

    <br><br>

    <a href="/logout">Logout</a>


    <br><br>

    <a href="/delete-account">
    Delete Account
    </a>


    """


@app.route("/download/<filename>")
@login_required
def download_file(filename):

    filename = secure_filename(filename)

    user_folder = os.path.join(
        "uploads",
        current_user.username
    )

    return send_from_directory(
        user_folder,
        filename,
        as_attachment=True
    )





@app.route("/share/<filename>")
@login_required
def share_file(filename):

    filename = secure_filename(filename)


    existing = SharedFile.query.filter_by(
        username=current_user.username,
        filename=filename
    ).first()

    if existing:
        return f"""
        <h1>Share Link</h1>
        <p>
        http://127.0.0.1:5000/shared/{existing.token}
        </p>
        """


    token = secrets.token_hex(16)

    shared = SharedFile(
        token=token,
        username=current_user.username,
        filename=filename
    )

    db.session.add(shared)
    db.session.commit()

    return f"""
    <h1>Share Link Created</h1>
    <p>
    http://127.0.0.1:5000/shared/{token}
    </p>
    """




@app.route("/unshare/<filename>")
@login_required
def unshare_file(filename):

    filename = secure_filename(filename)

    shared = SharedFile.query.filter_by(
        username=current_user.username,
        filename=filename
    ).first()

    if shared:
        db.session.delete(shared)
        db.session.commit()

    return "<h1>Sharing Disabled</h1>"

    




@app.route("/shared/<token>")
def shared_download(token):

    shared = SharedFile.query.filter_by(
        token=token
    ).first()

    if not shared:
        return "<h1>Invalid Share Link</h1>"

    user_folder = os.path.join(
        "uploads",
        shared.username
    )

    return send_from_directory(
        user_folder,
        shared.filename,
        as_attachment=True
    )






@app.route("/delete/<filename>")
@login_required
def delete_file(filename):
    

    filename = secure_filename(filename)
    file_path = os.path.join(
        "uploads",
        current_user.username,
        filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("dashboard"))







@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        file = request.files.get("file")

        if not file or file.filename == "":
            return "<h1>No file selected</h1>"

        user_folder = os.path.join(
            "uploads",
            current_user.username
        )

        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)

        current_usage = get_folder_size(user_folder)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if current_usage + file_size > MAX_STORAGE:
             return "<h1>Storage limit exceeded!</h1>"

        file.save(
            os.path.join(user_folder, filename)
        )

        return f"<h1>{filename} uploaded successfully!</h1>"

    return """
    <h1>Upload File</h1>

    <form method="POST" enctype="multipart/form-data">

        <input type="file" name="file">

        <br><br>

        <button type="submit">
            Upload
        </button>

    </form>
    """










@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/delete-account", methods=["GET", "POST"])
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

        return redirect(url_for("login"))

    return """
    <h1>Delete Account</h1>

    <p>
        This action is permanent.
        All files will be deleted.
    </p>

    <form method="POST">

        Password:

        <input
            type="password"
            name="password"
            required
        >

        <br><br>

        <button type="submit">
            Delete My Account
        </button>

    </form>

    <br>

    <a href="/dashboard">
        Cancel
    </a>
    """



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=False)
