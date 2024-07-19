import os


class Config:
    SECRET_KEY = os.getenv("SECRET")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///local.db")
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
