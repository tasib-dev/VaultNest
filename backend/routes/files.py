import os, secrets
from tools.storage import MAX_STORAGE, get_folder_size
from models import SharedFile, db
from flask import flash, Blueprint, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

files = Blueprint("files", __name__)



@files.route("/dashboard")
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

    file_list = []

    for file in files:
        shared = SharedFile.query.filter_by(
            username=current_user.username,
            filename=file
        ).first()

        if shared:
            action = f'<a href="/unshare/{file}">Stop Sharing</a>'
        else:
            action = f'<a href="/share/{file}">Share</a>'
        

        file_list.append({
            "filename": file,
            "shared": bool(shared)
            })
          





    return render_template(
        "dashboard.html",
        username=current_user.username,
        used_mb=used_mb,
        max_gb=max_gb,
        file_list=file_list
    )



@files.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        print("========== NEW UPLOAD ==========")
        print("Content-Length:", request.content_length)
        print("Files:", request.files)
        print("Form:", request.form)
        print("Content-Type:", request.content_type)

        file = request.files.get("file")

        print("file =", file)

        if not file:
            return "<h1>No file received</h1>"

        if file.filename == "":
            return "<h1>Filename missing</h1>"

        print("Filename:", file.filename)

        user_folder = os.path.join(
            "uploads",
            current_user.username
        )

        os.makedirs(user_folder, exist_ok=True)

        filename = secure_filename(file.filename)

        current_usage = get_folder_size(user_folder)

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        print("Detected size:", file_size)
        file.seek(0)

        if current_usage + file_size > MAX_STORAGE:
            flash("Storage limit exceeded!")
            return redirect(url_for("files.dashboard"))

        file.save(
            os.path.join(user_folder, filename)
        )

        flash("uploaded successfully!")
        return redirect(url_for("files.dashboard"))

    return render_template("upload.html")
    
    
    

@files.route("/download/<filename>")
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


@files.route("/download/app.apk")
@login_required
def download_app():

    apk_path = os.path.join(
        "updates",
        "app.apk"
    )

    return send_file(
        apk_path,
        as_attachment=True,
        download_name="app.apk",
        mimetype="application/vnd.android.package-archive"
    )




@files.route("/delete/<filename>")
@login_required
def delete_file(filename):

    
    print("DELETE ROUTE HIT:", filename)

    filename = secure_filename(filename)

    


    file_path = os.path.join(
        "uploads",
        current_user.username,
        filename
    )


    


    if os.path.exists(file_path):

        os.remove(file_path)

        
    flash("deleted successfully!!!")    
    return redirect(url_for("files.dashboard"))
    

@files.route("/share/<filename>")
@login_required
def share_file(filename):

    filename = secure_filename(filename)


    existing = SharedFile.query.filter_by(
        username=current_user.username,
        filename=filename
    ).first()

    if existing:
        share_url = url_for(
            "files.shared_download",
            token=existing.token,
            _external=True
        )

        return render_template(
            "share.html",
            share_url=share_url
        )

    token = secrets.token_hex(16)

    shared = SharedFile(
        token=token,
        username=current_user.username,
        filename=filename
    )

    db.session.add(shared)
    db.session.commit()

    share_url = url_for(
        "files.shared_download",
        token=token,
        _external=True
    )

    return render_template(
        "share.html",
        share_url=share_url
    )



@files.route("/unshare/<filename>")
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

    flash("Sharing disabled successfully!")
    return redirect(url_for("files.dashboard"))
   


@files.route("/shared/<token>")
def shared_download(token):

    shared = SharedFile.query.filter_by(
        token=token
    ).first()

    if not shared:
        return render_template("invalid_share.html")

    return render_template(
        "shared_file.html",
        filename=shared.filename,
        username=shared.username,
        token=token
    ) 

@files.route("/shared/<token>/download")
def download_shared_file(token):

    shared = SharedFile.query.filter_by(
        token=token
    ).first()

    if not shared:
        return render_template("invalid_share.html")

    user_folder = os.path.join(
        "uploads",
        shared.username
    )

    return send_from_directory(
        user_folder,
        shared.filename,
        as_attachment=True
    )
