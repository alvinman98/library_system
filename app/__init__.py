from flask import Flask
from .db import db, migrate
from .routes import register_routes
from flask_jwt_extended import JWTManager
from app.routes import auth, user, books
from app.routes import cart


jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    
    jwt.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    register_routes(app)

    return app
