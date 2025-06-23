# app/__init__.py
from flask import Flask
from app.routes.user_routes import user_bp
from app.routes.employee_profile_routes import profile_bp
from app.utils.logger import logger

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.register_blueprint(user_bp)
    app.register_blueprint(profile_bp)
    logger.info("Flask App Initialized.")
    return app
