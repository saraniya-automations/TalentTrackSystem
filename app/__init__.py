# # app/__init__.py
# from flask import Flask
# from app.routes.user_routes import user_bp
# from app.utils.logger import logger
# from flask_jwt_extended import JWTManager

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object('app.config.Config')
#     app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'  

#     JWTManager(app)
#     app.register_blueprint(user_bp)
#     logger.info("Flask App Initialized.")
#     return app

# app/__init__.py

from flask import Flask
from app.routes.user_routes import user_bp
from app.routes.employee_profile_routes import profile_bp
from app.routes.leave_routes import leave_bp #Added for leave
from app.utils.logger import logger
from app.config import Config
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app(testing=False):
    app = Flask(__name__)
    
    if testing:
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    else:
        app.config.from_object(Config)

    jwt.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(leave_bp) #Added for leave feature
    logger.info("Flask App Initialized.")

    return app
