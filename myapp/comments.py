from .models import User, Video, Comment, Like
from flask import Blueprint

comment = Blueprint("comment", __name__)


@comment.route("/watch/<string:unique_name>")
def comment(unique_name):
    return ""
