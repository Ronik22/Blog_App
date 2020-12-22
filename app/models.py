from app import db
from datetime import datetime

class users(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), default='N/A')
    datetime = db.Column(db.String(100), default='N/A')
    imgurl = db.Column(db.String(100), nullable=False, default='app/static/images/defprof.png')

    def __init__(self, name, email, datetime, pwd, imgurl):
        self.name = name
        self.email = email
        self.pwd = pwd
        self.datetime = datetime
        self.imgurl = imgurl

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30), nullable=False, default='N/A')
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id)