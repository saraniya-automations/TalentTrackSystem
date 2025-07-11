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
from app.routes.leave_routes import leave_bp
from app.routes.performance_routes import performance_bp
from app.routes.attendance_routes import attendance_bp
from app.routes.salary_routes import salary_bp 
from app.routes.admin_dashboard_routes import admin_bp
from app.routes.employee_dashboard_routes import employee_dashboard_bp

from app.utils.logger import logger
from app.config import Config
from flask_jwt_extended import JWTManager
from flask_cors import CORS

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
    app.register_blueprint(leave_bp)
    app.register_blueprint(performance_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(employee_dashboard_bp)
    logger.info("Flask App Initialized.")

        # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins — change this to specific origin if needed

    # Insert dummy admin user and profile
    with app.app_context():
        # from app.utils.seed import insert_dummy_admin
        # insert_dummy_admin()
        from app.utils.seed import seed_database
        seed_database()

    with app.app_context():
         from app.utils.seed import insert_default_courses
         insert_default_courses()

    return app
