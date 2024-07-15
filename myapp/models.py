from flask_login import UserMixin
from sqlalchemy.orm import backref
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000))
    videos = db.relationship("Video", backref="user", lazy=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_title = db.Column(db.String(100), nullable=False)
    video_desc = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(100))

    file_path = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, file_path, video_title, video_desc, file_name, user_id):
        self.video_title = video_title
        self.video_desc = video_desc
        self.file_name = file_name

        self.file_path = file_path
        self.user_id = user_id
