from flask import Flask, current_app
import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO


db = SQLAlchemy()
login_manager = LoginManager()
sock = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    app.config["UPLOAD_EXTENSIONS"] = [
        ".mp4",
        ".avi",
        ".mov",
    ]
    filepath = os.path.join(app.root_path, "temp")
    app.config["UPLOAD_FOLDER"] = filepath

    db.init_app(app)
    Migrate(app, db)

    sock.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth

    app.register_blueprint(auth)

    from .home import home

    app.register_blueprint(home)

    from .video import video

    app.register_blueprint(video)

    return app
