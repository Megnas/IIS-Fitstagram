from flask import Flask
from dotenv import load_dotenv
import os

from modules.db import db

app = Flask(__name__)

#Load env from .env
load_dotenv()
#Get db url form env
db_path = os.getenv('DATABASE_URL')
print("Db: ", db_path)
#Set db param (if env does not exist, will default to "sqlite:///project.db")
app.config["SQLALCHEMY_DATABASE_URI"] = db_path if db_path else "sqlite:///project.db"


with  app.app_context():
    db.init_app(app)
    db.create_all()

@app.route("/")
def main():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")