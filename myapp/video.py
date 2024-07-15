# video.py
from aiortc.rtcpeerconnection import asyncio, uuid
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    Response,
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

video = Blueprint("video", __name__)


@sock.on("offer")
def handle_offer(offer):
    emit("offer", offer, broadcast=True, include_self=False)


@sock.on("answer")
def handle_answer(answer):
    emit("answer", answer, broadcast=True, include_self=False)


@sock.on("ice_candidate")
def handle_ice_candidate(ice_candidate):
    emit("ice_candidate", ice_candidate, broadcast=True, include_self=False)


def get_file_path(file_name):
    path = os.path.join(current_app.root_path, "temp", file_name)
    return path


@video.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        video_title = request.form.get("video_title")
        video_desc = request.form.get("video_desc")
        file = request.files.get("file")
        if file:
            filename = secure_filename(file.filename)
            if filename != "":
                file_ext = os.path.splitext(filename)[1]
                if file_ext.lower() in current_app.config["UPLOAD_EXTENSIONS"]:
                    # Read the file data
                    file_data = file.read()

                    # Create a new Video object
                    new_video = Video(
                        video_title=video_title,
                        video_desc=video_desc,
                        file_name=filename,
                        file_path=get_file_path(filename),
                        user_id=current_user.id,
                    )

                    # Add to database and commit
                    db.session.add(new_video)
                    db.session.commit()

                    print("Upload successful")
                    return redirect(url_for("home.profile", video_id=new_video.id))
                else:
                    return "Invalid file extension", 400
            else:
                return "No file selected", 400
    return render_template("upload.html")
