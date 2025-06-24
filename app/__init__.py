# app/__init__.py
from flask import Flask
from app.routes.user_routes import user_bp
from app.utils.logger import logger
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'  

    JWTManager(app)
    app.register_blueprint(user_bp)
    logger.info("Flask App Initialized.")
    return app
