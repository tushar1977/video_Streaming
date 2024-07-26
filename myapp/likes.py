from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required
from flask_login.login_manager import flash, redirect
from . import db
from .models import Like, Video

like = Blueprint("like", __name__)


@like.route("/api/<string:likes>/<string:unique_name>", methods=["POST"])
@login_required
def like_action(like_type, unique_name):
    video = Video.query.get_or_404(unique_name)
    existing_like = Like.query.filter_by(
        user_id=current_user.id, video_id=unique_name
    ).first()

    if existing_like:
        if existing_like.like_type == unique_name:
            db.session.delete(existing_like)
            flash("Your rating has been removed.")
        else:
            existing_like.like_type = unique_name
            flash("Your rating has been updated.")
    else:
        new_like = Like(
            like_type=like_type, user_id=current_user.id, video_id=unique_name
        )
        db.session.add(new_like)
        flash("Your rating has been added.")
    db.session.commit()
    return redirect(url_for("video.watch_video", unique_name=unique_name))
