from flask import Flask
from app.routes.user_routes import user_bp
from app.routes.leave_routes import leave_bp
from app.routes.employee_profile_routes import profile_bp
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app(testing=False):
    app = Flask(__name__)
    from app.config import Config
    app.config.from_object(Config)

    if testing:
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    jwt.init_app(app)

    # Register all blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(profile_bp)

    return app
