import os
from flask import Blueprint, current_app, redirect, url_for
from flask.templating import render_template
from flask_login import current_user, login_required
from .models import User, Video

home = Blueprint("home", __name__)


def get_file_path(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER_IMAGE"]
    return os.path.join(upload_folder, filename)


@home.route("/", methods=["GET"])
def index():
    videos = Video.query.all()
    for video in videos:
        thumbnail_url = url_for("static", filename=f"img/{video.thumbnail_name}")

        thumbnail_full_path = os.path.join(
            current_app.root_path, thumbnail_url.lstrip("/")
        )

        video.thumbnail_url = thumbnail_full_path
        print(video.thumbnail_url)  # For debugging purposes

    return render_template("index.html", videos=videos)


@home.route("/profile", methods=["GET"])
@login_required
def profile():
    user = User.query.get(current_user.id)
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", name=user.name, videos=videos)
