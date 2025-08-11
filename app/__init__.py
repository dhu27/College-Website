from flask import Flask
from app.db import db
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate(app, db) # initialize flask-migrate
    login_manager.init_app(app)  # ✅ after app is created
    login_manager.login_view = 'auth.login' # Set the login view for Flask-Login

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register routes/blueprints here
    from app.routes.main import main_bp
    from app.routes.colleges import colleges_bp
    from app.routes.auth import auth_bp
    from app.routes.recommendations import recommendations_bp
    from app.routes.lists import lists_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(colleges_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(lists_bp)

    return app
