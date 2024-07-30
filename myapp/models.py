from flask_login import UserMixin, current_user
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import backref
from . import db
import re
import bcrypt
from sqlalchemy.dialects.mysql import ENUM


class Video(db.Model):
    video_title = db.Column(db.String(100), nullable=False)
    video_desc = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(100))
    thumbnail_name = db.Column(db.String(100))
    unique_name = db.Column(
        db.String(10), unique=True, nullable=False, primary_key=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="video", lazy=True)
    likes = db.relationship("Like", backref="video", lazy=True)

    def __init__(
        self, thumbnail_name, video_title, video_desc, file_name, user_id, unique_name
    ):
        self.video_title = video_title
        self.video_desc = video_desc
        self.file_name = file_name
        self.thumbnail_name = thumbnail_name
        self.user_id = user_id
        self.unique_name = unique_name

    def get_user_like(self):
        if current_user.is_authenticated:
            return Like.query.filter_by(
                user_id=current_user.id, video_id=self.unique_name
            ).first()
        return None


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    video_id = db.Column(
        db.String(10), db.ForeignKey("video.unique_name"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    def __init__(self, text, user_id, video_id):
        self.text = text
        self.user_id = user_id
        self.video_id = video_id


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    like_type = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    video_id = db.Column(
        db.String(10), db.ForeignKey("video.unique_name"), nullable=False
    )
    __table_args__ = (
        CheckConstraint(like_type.in_(["like", "dislike"]), name="check_like_type"),
    )

    def __init__(self, like_type, user_id, video_id):
        self.like_type = like_type
        self.user_id = user_id
        self.video_id = video_id

    def __repr__(self):
        return f"<Like {self.id}: {self.like_type} by User {self.user_id} on Video {self.video_id}>"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000))
    comments = db.relationship("Comment", backref="user", lazy=True)
    videos = db.relationship("Video", backref="User", lazy=True)
    likes = db.relationship("Like", backref="User", lazy=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

    @staticmethod
    def is_valid_email(email):
        allowed_domains = [
            "gmail.com",
            "googlemail.com",
            "yahoo.com",
            "ymail.com",
            "rocketmail.com",
            "outlook.com",
            "hotmail.com",
            "live.com",
            "msn.com",
            "icloud.com",
            "me.com",
            "mac.com",
            "aol.com",
            "protonmail.com",
            "protonmail.ch",
            "zoho.com",
            "zohomail.com",
            "mail.com",
            "email.com",
            "usa.com",
            "europe.com",
            "asia.com",
            "mweb.co.za",
            "online.nl",
            "post.com",
            "shortmail.com",
            "coach.com",
            "consultant.com",
            "engineer.com",
            "doctor.com",
            "gmx.com",
            "gmx.de",
            "gmx.net",
            "yandex.com",
            "yandex.ru",
            "tutanota.com",
            "tutanota.de",
            "mail.ru",
            "list.ru",
            "bk.ru",
            "inbox.ru",
        ]

        # Create the regex pattern
        domain_pattern = "|".join(re.escape(domain) for domain in allowed_domains)
        regex_pattern = rf"^[a-zA-Z0-9_.+-]+@({domain_pattern})$"
        return re.match(regex_pattern, email) is not None

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))
