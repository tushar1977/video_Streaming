import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    UPLOAD_FOLDER_IMAGE = os.path.join(os.getcwd(), "myapp", "static", "img")
    SEND_FILE_MAX_AGE_DEFAULT = 0

    UPLOAD_FOLDER_VIDEO = os.path.join(os.getcwd(), "myapp", "static", "video")
    UPLOAD_EXTENSIONS = [
        ".mp4",
        ".avi",
        ".mov",
        ".jpeg",
        ".png",
        ".jpg",
    ]
