from flask import Flask, render_template, request
from flask_login import current_user
from dotenv import load_dotenv
import os
from modules.db import db, Roles
from modules.auth import init_login_manager
import modules.photo_manager as pm
import modules.user_manager as um
import click

app = Flask(__name__)

def str_to_bool(value):
    return str(value).lower() in {'true', '1', 't', 'yes', 'y'}


load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL', "sqlite:///project.db")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "not very secret key")
app.config['ALLOW_REGISTRATION'] = str_to_bool(os.getenv('ALLOW_REGISTRATION', "True"))

@app.cli.command("purge-db")
def purge_db():
    """Purges all data from all database tables."""
    meta = db.metadata
    with app.app_context():
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    db.metadata.clear()
    db.drop_all()
    db.session.commit()
    click.echo("All tables have been purged.")

@app.cli.command("create-admin")
def purge_db():
    """Purges all data from all database tables."""
    meta = db.metadata
    with app.app_context():
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
    db.metadata.clear()
    db.drop_all()
    db.session.commit()
    click.echo("Created admin user.")

with  app.app_context():
    db.init_app(app)
    #db.drop_all()
    db.create_all()
    init_login_manager(app)

from modules import auth_template, view_template, settings_template, groups_template, photo_template, post_template, search_template, admin_template
app.register_blueprint(auth_template.bp)
app.register_blueprint(photo_template.bp)
app.register_blueprint(view_template.bp)
app.register_blueprint(settings_template.bp)
app.register_blueprint(groups_template.bp)
app.register_blueprint(post_template.bp)
app.register_blueprint(search_template.bp)
app.register_blueprint(admin_template.bp)

@app.context_processor
def inject_user():
    return {'user': current_user}

@app.context_processor
def utility_functions():
    #retuns user object from id
    def get_user(usr_id: int):
        return um.get_user(usr_id)
    def current_user_is_moderator():
        if not current_user.is_authenticated:
            return False
        return current_user.role == Roles.MODERATOR or current_user.role == Roles.ADMIN
    def current_user_is_admin():
        if not current_user.is_authenticated:
            return False
        return current_user.role == Roles.ADMIN
    def modify_query_params(**kwargs):
        """Helper function to modify query parameters dynamically."""
        args = request.args.to_dict()  # Get current query parameters
        args.update(kwargs)  # Update with new parameters
        return f"{request.path}?{'&'.join([f'{k}={v}' for k, v in args.items()])}"
    return dict(
        get_user=get_user, 
        modify_query_params=modify_query_params,
        current_user_is_moderator=current_user_is_moderator,
        current_user_is_admin=current_user_is_admin
    )

@app.errorhandler(Exception)
def universal_error_handler(e):
    if hasattr(e, 'code'):
        error_code = e.code
        error_name = e.name
    else:
        error_code = 500
        error_name = "Internal Server Error"

    return render_template('error.html', error_name=error_name, error_message=str(e)), error_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")