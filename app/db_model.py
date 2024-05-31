# Copyright 2024 Marcelo Sanches
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from flask_login import UserMixin
#from flask_wtf.csrf import CSRFProtect
from jsonschema import validate

# custom
from . import db

# table models
class User(db.Model, UserMixin):
    """Dynamic: filled as users signup"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
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
    hint = db.Column(db.String(255))
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

score_schema = {
    "type": "array",
    "items": {"type": "number"}
}

class Answer(db.Model):
    """Dynamic: filled as users answer questions and select models"""
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pun_id = db.Column(db.Integer, db.ForeignKey('puns.id'), nullable=False)
    # user answer & score compared to pun answer
    user_answer = db.Column(db.String(100), nullable=False)
    # store scores as a JSON-encoded string
    scores = db.Column(db.String, nullable=False)
    # weighted avg score (based on previous weights in models & scores)
    avg_score = db.Column(db.Float)
    # T/F for whether user guessed correctly or not
    correct_guess = db.Column(db.Boolean)
    # user response confirming Y/N for the reaction (the deemed 'correct' guess)
    user_confirmed_as = db.Column(db.String)
    # id of selected model (best model, to be incremented in Models.num_votes)
    selected_model = db.Column(db.Integer)

    def __init__(
            self
            , user_id
            , pun_id
            , user_answer
            , scores
            , avg_score
            , correct_guess
            , user_confirmed_as
            , selected_model
        ):
        validate(instance=scores, schema=score_schema)
        self.user_id = user_id
        self.pun_id = pun_id
        self.user_answer = user_answer
        self.scores = json.dumps(scores)
        self.avg_score = avg_score
        self.correct_guess = correct_guess
        self.user_confirmed_as = user_confirmed_as
        self.selected_model = selected_model
