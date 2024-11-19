from flask import Flask, render_template
from dotenv import load_dotenv
import os
from modules.db import db
from modules.auth import init_login_manager

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

with  app.app_context():
    db.init_app(app)
    #db.drop_all()
    db.create_all()
    init_login_manager(app)

from modules import auth_template
app.register_blueprint(auth_template.bp)

@app.route("/")
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")