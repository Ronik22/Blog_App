from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)

from app import views, models