import cv2
from flask import (
    Blueprint,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
)
from flask.helpers import flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .models import Video
import random
from . import db
import string
import re

video = Blueprint("video", __name__)


def get_chunk(file_path, byte1=None, byte2=None):

    file_size = os.stat(file_path).st_size
    start = 0 if byte1 is None else byte1
    end = file_size - 1 if byte2 is None else byte2
    length = end - start + 1

    with open(file_path, "rb") as f:
        f.seek(start)
        chunk = f.read(length)

    return chunk, start, end, file_size


def get_file_path(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER_VIDEO"]
    return os.path.join(upload_folder, filename)


@video.route("/watch/<string:unique_name>")
def stream_video(unique_name):
    video = Video.query.filter_by(unique_name=unique_name).first_or_404()
    file_path = get_file_path(video.file_name)
    range_header = request.headers.get("Range", None)
    byte1, byte2 = 0, None

    if range_header:
        match = re.search(r"(\d+)-(\d*)", range_header)
        if match:
            groups = match.groups()
            byte1, byte2 = int(groups[0]), (int(groups[1]) if groups[1] else None)

    chunk, start, end, file_size = get_chunk(file_path, byte1, byte2)
    resp = Response(chunk, 206, mimetype="video/mp4", content_type="video/mp4")
    resp.headers.add("Content-Range", f"bytes {start}-{end}/{file_size}")
    return resp


@video.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        video_title = request.form.get("video_title")
        video_desc = request.form.get("video_desc")
        thumbnail = request.files.get("img")
        password = "".join(random.choice(string.printable) for i in range(8))
        file = request.files.get("file")
        if file:
            filename = secure_filename(file.filename)
            imgname = secure_filename(thumbnail.filename)
            if filename != "" and imgname != "":
                file_ext = os.path.splitext(filename)[1]
                img_ext = os.path.splitext(imgname)[1]
                if (
                    file_ext.lower() in current_app.config["UPLOAD_EXTENSIONS"]
                    and img_ext.lower() in current_app.config["UPLOAD_EXTENSIONS"]
                ):
                    # file_path = get_file_path(filename)
                    # img_path = get_file_path(imgname)
                    try:
                        file.save(
                            os.path.join(
                                current_app.config["UPLOAD_FOLDER_VIDEO"], filename
                            )
                        )
                        thumbnail.save(
                            os.path.join(
                                current_app.config["UPLOAD_FOLDER_IMAGE"], imgname
                            )
                        )

                        new_video = Video(
                            video_title=video_title,
                            video_desc=video_desc,
                            file_name=filename,
                            thumbnail_name=imgname,
                            user_id=current_user.id,
                            unique_name=password,
                        )
                        # Add to database and commit
                        db.session.add(new_video)
                        db.session.commit()
                        flash("Upload successful")
                        return redirect(url_for("home.profile", video_id=new_video.id))
                    except Exception as e:
                        print(f"Error saving file: {e}")
                        return "Internal server error", 500
                else:
                    return "Invalid file extension", 400
            else:
                return "No file selected", 400
    return render_template("upload.html")
