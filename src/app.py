from flask import Flask, render_template, request
from flask_login import current_user
from dotenv import load_dotenv
import os
from modules.db import db
from modules.auth import init_login_manager
import modules.photo_manager as pm

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
    """
    Purges all data from the database.
    WARNING: This action is irreversible.
    """
    try:
        # Drop all tables
        db.drop_all()

        # Recreate tables
        db.create_all()

        print("Database purged successfully!")
    except Exception as e:
        print(f"Error while purging the database: {e}")

with  app.app_context():
    db.init_app(app)
    #db.drop_all()
    db.create_all()
    init_login_manager(app)

from modules import auth_template, foto_template, view_template, settings_template
app.register_blueprint(auth_template.bp)
app.register_blueprint(foto_template.bp)
app.register_blueprint(view_template.bp)
app.register_blueprint(settings_template.bp)

@app.context_processor
def inject_user():
    return {'user': current_user}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")