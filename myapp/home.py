from flask import Blueprint, redirect, url_for
from flask.templating import render_template
from flask_login import current_user, login_required
from .models import User, Video

home = Blueprint("home", __name__)


@home.route("/watch/<string:unique_name>", methods=["GET"])
def watch_video(unique_name):
    video = Video.query.filter_by(unique_name=unique_name).first_or_404()
    return render_template("watch.html", video=video)


@home.route("/", methods=["GET"])
def index():
    video = Video.query.all()
    return render_template("index.html", video=video)


@home.route("/profile", methods=["GET"])
@login_required
def profile():
    user = User.query.get(current_user.id)
    videos = Video.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", name=user.name, videos=videos)
