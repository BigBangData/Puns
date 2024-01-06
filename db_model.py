from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask import Flask

# setup flask app
app = Flask(__name__)
# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

# setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwu#$)_@34FmkmKHDF02'

# troubleshoot creating new database
#if 'sqlalchemy' in app.extensions:
#    del app.extensions['sqlalchemy']

# instantiate database
db = SQLAlchemy(app)

# table models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    # define relationship to the "answers" table
    answers = db.relationship('Answer', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer = db.Column(db.String(100), nullable=False)
    user_answer = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)