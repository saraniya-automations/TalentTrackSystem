from flask import Flask
from app.routes.user_routes import user_bp
from app.routes.leave_routes import leave_bp
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app(testing=False):
    app = Flask(__name__)
    
    from app.config import Config
    app.config.from_object(Config)

    if testing:
        app.config['TESTING'] = True
        app.config['DATABASE'] = ':memory:'  # Use in-memory DB for tests
        app.config['JWT_SECRET_KEY'] = 'test-key'

    jwt.init_app(app)
    app.register_blueprint(user_bp)
    app.register_blueprint(leave_bp)

    return app
