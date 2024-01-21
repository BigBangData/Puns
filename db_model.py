import json
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

# uncomment for creating new database from scratch
if 'sqlalchemy' in app.extensions:
   del app.extensions['sqlalchemy']

# instantiate database
db = SQLAlchemy(app)

# table models
class User(db.Model, UserMixin):
    """Dynamic: filled as users signup"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    # define relationship to the "answers" table
    answers = db.relationship('Answer', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Puns(db.Model):
    """Static: filled by insert_into_puns()"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    # define relationship to the "answers" table
    answers = db.relationship('Answer', backref='puns', lazy=True)

class Models(db.Model):
    """Static: initial fill by insert_into_models()
        Dynamic: votes filled as users select best models
    """
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(255), nullable=False)
    long_name = db.Column(db.String(255), nullable=False)
    num_votes = db.Column(db.Integer)
    # define relationship to the "answers" table
    answers = db.relationship('Answer', backref='models', lazy=True)

class Answer(db.Model):
    """Dynamic: filled as users answer questions and select models"""
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pun_id = db.Column(db.Integer, db.ForeignKey('puns.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'))
    # user answer & score compared to pun answer
    user_answer = db.Column(db.String(100), nullable=False)
    # store scores as a JSON-encoded string
    scores = db.Column(db.String, nullable=False)
    # id of selected model
    selected_model = db.Column(db.Integer)

    def __init__(self, user_id, pun_id, user_answer, scores, selected_model):
        self.user_id = user_id
        self.pun_id = pun_id
        self.user_answer = user_answer
        self.scores = json.dumps(scores)
        self.selected_model = selected_model
