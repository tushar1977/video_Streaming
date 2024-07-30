from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required
from flask_login.login_manager import flash, redirect
from . import db
from .models import Like, Video

like = Blueprint("like", __name__)


@like.route("/like_action/<string:like_action>/<string:unique_name>", methods=["POST"])
@login_required
def like_action(like_action, unique_name):
    video = Video.query.filter_by(unique_name=unique_name).first_or_404()
    existing_like = Like.query.filter_by(
        user_id=current_user.id, video_id=unique_name
    ).first()

    if like_action == "like":
        if existing_like:
            # If like already exists, remove it (toggle off)
            db.session.delete(existing_like)
        else:
            # If no like exists, add a new one
            new_like = Like(
                user_id=current_user.id, video_id=unique_name, like_type="like"
            )
            db.session.add(new_like)

    db.session.commit()
    return redirect(url_for("video.watch_video", unique_name=unique_name))
