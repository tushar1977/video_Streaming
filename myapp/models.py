from flask_login import UserMixin
from . import db
import re
import bcrypt


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


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_title = db.Column(db.String(100), nullable=False)
    video_desc = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(100))

    thumbnail_name = db.Column(db.String(100))

    unique_name = db.Column(db.String(10))
    # file_path = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(
        self, thumbnail_name, video_title, video_desc, file_name, user_id, unique_name
    ):
        self.video_title = video_title
        self.video_desc = video_desc
        self.file_name = file_name

        self.thumbnail_name = thumbnail_name

        self.user_id = user_id
        self.unique_name = unique_name
