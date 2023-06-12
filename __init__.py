from flask import Flask
from config import HOST, PASSWORD, USERNAME, DATABASE_NAME
import flask_sqlalchemy
from flask_login import LoginManager


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
db = flask_sqlalchemy.SQLAlchemy(app)
