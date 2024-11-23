from flask import Flask, render_template, request
from flask_login import current_user
from dotenv import load_dotenv
import os
from modules.db import db
from modules.auth import init_login_manager
import modules.photo_manager as pm
import modules.user_manager as um
import click

app = Flask(__name__)

#Load env from .env
load_dotenv()
#Get db url form env
db_path = os.getenv('DATABASE_URL')
print("Db: ", db_path)
#Set db param (if env does not exist, will default to "sqlite:///project.db")
app.config["SQLALCHEMY_DATABASE_URI"] = db_path if db_path else "sqlite:///project.db"

#TODO: Load secret key from .env
app.config['SECRET_KEY'] = 'not a secret'

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

with  app.app_context():
    db.init_app(app)
    #db.drop_all()
    db.create_all()
    init_login_manager(app)

from modules import auth_template, view_template, settings_template, groups_template, photo_template, post_template
app.register_blueprint(auth_template.bp)
app.register_blueprint(photo_template.bp)
app.register_blueprint(view_template.bp)
app.register_blueprint(settings_template.bp)
app.register_blueprint(groups_template.bp)
app.register_blueprint(post_template.bp)

@app.context_processor
def inject_user():
    return {'user': current_user}

@app.context_processor
def utility_functions():
    #retuns user object from id
    def get_user(usr_id: int):
        return um.get_user(usr_id)
    return dict(get_user=get_user)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")