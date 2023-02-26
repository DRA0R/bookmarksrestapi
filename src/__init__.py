from flask import Flask
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:

        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI"),
            JWT_SECRET_KEY= os.environ.get("JWT_SECRET_KEY")
        )

    else:
        app.config.from_mapping(test_config)

    db.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    JWTManager(app)

    @app.get("/")
    def index():
        return "Hello, word!"

    @app.get("/hello")
    def sayhello():
        return {"message": "Hello, word!"}

    return app