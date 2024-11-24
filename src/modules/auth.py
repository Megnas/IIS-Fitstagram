from flask import Flask
from flask_login import LoginManager
from .db import User

# Initialize LoginManager
login_manager = LoginManager()

def init_login_manager(app: Flask):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.filter_by(id=user_id, blocked = False).first()
        except:
            return None