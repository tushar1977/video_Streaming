import cv2
from flask import (
    Blueprint,
    Response,
    send_from_directory,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user
from flask_socketio import emit
from werkzeug.utils import secure_filename
import os
from . import db, sock
from .models import Video
import random
import string
import re

video = Blueprint("video", __name__)


def get_chunk(file_path, byte1=None, byte2=None):
    full_path = os.path.join(file_path)
    file_size = os.stat(full_path).st_size
    start = 0 if byte1 is None else byte1
    end = file_size - 1 if byte2 is None else byte2
    length = end - start + 1

    with open(full_path, "rb") as f:
        f.seek(start)
        chunk = f.read(length)

    return chunk, start, end, file_size


def get_file_path(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return os.path.join(upload_folder, filename)


@video.route("/watch/<string:unique_name>")
def stream_video(unique_name):
    video = Video.query.filter_by(unique_name=unique_name).first_or_404()
    file_path = secure_filename(video.file_path)
    print(file_path)
    range_header = request.headers.get("Range", None)
    byte1, byte2 = 0, None

    if range_header:
        match = re.search(r"(\d+)-(\d*)", range_header)
        if match:
            groups = match.groups()
            byte1, byte2 = int(groups[0]), (int(groups[1]) if groups[1] else None)

    chunk, start, end, file_size = get_chunk(file_path, byte1, byte2)
    print(file_path)
    resp = Response(chunk, 206, mimetype="video/mp4", content_type="video/mp4")
    resp.headers.add("Content-Range", f"bytes {start}-{end}/{file_size}")
    print(resp)
    return resp


@video.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        video_title = request.form.get("video_title")
        video_desc = request.form.get("video_desc")
        password = "".join(random.choice(string.printable) for i in range(8))
        file = request.files.get("file")
        if file:
            filename = secure_filename(file.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext.lower() in current_app.config["UPLOAD_EXTENSIONS"]:
                    file_path = get_file_path(filename)
                    try:
                        # Ensure the upload folder exists
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        # Save the file
                        file.save(file_path)
                        # Create a new Video object
                        new_video = Video(
                            video_title=video_title,
                            video_desc=video_desc,
                            file_name=filename,
                            file_path=file_path,
                            user_id=current_user.id,
                            unique_name=password,
                        )
                        # Add to database and commit
                        db.session.add(new_video)
                        db.session.commit()
                        print("Upload successful")
                        return redirect(url_for("home.profile", video_id=new_video.id))
                    except Exception as e:
                        print(f"Error saving file: {e}")
                        return "Internal server error", 500
                else:
                    return "Invalid file extension", 400
            else:
                return "No file selected", 400
    return render_template("upload.html")
