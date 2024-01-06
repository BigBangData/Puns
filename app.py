import os
import csv
import spacy
import random
import logging

from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# custom import
from db_model import app, db, User, Answer

# setup logging for file and console
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file = os.path.join('logs', f"{datetime.now().strftime('%Y%m%d_%H%M%SMT')}.log")
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(log_format)
console_handler.setFormatter(formatter)

# User
# security & login
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# reload user object from user_id stored in session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Answer
# Load English model to compare answers
# downloaded with: python -m spacy download en_core_web_md
nlp = spacy.load("en_core_web_md")

def compare_texts(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    # compute similary score
    score = doc1.similarity(doc2)
    # compare with threshold
    # return 1 if score >= threshold else 0
    return score

def store_answer(user_answer, answer, score):
    new_answer = Answer(
        user_id=current_user.id,
        answer=answer,
        user_answer=user_answer,
        score=score
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()

class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)]
        , render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)]
        , render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Signup")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("User exists.")

class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)]
        , render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)]
        , render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Login")


# home
@app.route('/')
def home():
    return render_template('index.html')

# signup
@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            msg = f"Created new account for {form.username.data}. Please login."
            logging.info(msg=msg)
            flash(msg, "info")
            return redirect(url_for('login'))
        else:
            msg = f"Username '{form.username.data}' exists. Please try another."
            logging.info(msg=msg)
            flash(msg, "info")
            return render_template("signup.html", form=form)
    # "GET"
    else:
        try:
            msg = f"You're currently logged in as {current_user.username}. \
                Please log out before signing up with another username."
            flash(msg, "info")
            return redirect(url_for('view'))
        # throws error when current_user is Anonymous (not logged in)
        except AttributeError:
            return render_template('signup.html', form=form)

# login
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user_id = User.query.filter_by(username=form.username.data).first()
            if user_id:
                if bcrypt.check_password_hash(user_id.password, form.password.data):
                    login_user(user_id)
                    flash(f"Hello {user_id.username}, you are logged in.", "info")
                    return redirect(url_for('view'))
                else:
                    logging.info(msg=f"Wrong password for {form.username.data}.")
                    flash("Wrong password.", "info")
                    return render_template('login.html', form=form)
            else:
                flash("Did you signup for an account yet?", "info")
                return redirect(url_for('signup'))
    # "GET"
    else:
        # cannot do "if current_user" since it exists, yet has no username
        try:
            msg = f"{current_user.username}, you're already logged in."
            flash(msg, "info")
            return redirect(url_for('view'))
        # throws error when current_user = AnonymousUserMixin
        except AttributeError:
            return render_template('login.html', form=form)

# logout
@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash("You've logged out.", "info")
    return redirect(url_for('login'))

def get_pun():
    if 'question' not in session or 'answer' not in session:
        # load static puns.csv
        csv_file_path = os.path.join('static', 'files', 'puns.csv')
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                puns_list = list(csv_reader)
                # select random pun joke
                random_pun = random.choice(puns_list)
                # separate into question and answer
                question = f"{random_pun['question']}?"
                answer = f"{random_pun['answer']}"
                # add to session to persist specific pair
                session['question'] = question
                session['answer'] = answer
        except FileNotFoundError:
            logging.error(f"CSV file '{csv_file_path}' not found.")
    else:
        question = session['question']
        answer = session['answer']
    # return new ones or same ones if already in session
    return question, answer

# view
@app.route('/view', methods=["POST", "GET"])
@login_required
def view():
    if request.method == "POST":
        # clear session variables related to question and answer
        session.pop('question', None)
        session.pop('answer', None)
        return redirect(url_for('view_answer'))
    else:
        question, _ = get_pun()
        return render_template('view.html', values=[question])

# Define get_reaction_message function first
def get_reaction_message(score):
    if score >= 0.8:
        return "Punbelievable, you're on fire!"
    elif 0.6 <= score < 0.8:
        return "Punderful job."
    else:
        return "Hm, that wasn't puntastic."

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    # get session answer
    _, answer = get_pun()
    if request.method == "POST":
        # make sure text area is completed
        user_answer = request.form.get('user_answer')
        if not user_answer.strip():
            flash("Text area cannot be empty.", "info")
            return redirect(url_for('view'))
        else:
            # get score for text comparison
            score = compare_texts(user_answer, answer)
            # store data in answer table
            store_answer(user_answer, answer, score)
            # determine reaction based on the score
            reaction_msg = get_reaction_message(score)
            # flash(reaction_msg)
            return render_template('view_answer.html', values=[reaction_msg, answer])
    else:
        return redirect(url_for('view'))


if __name__ == '__main__':
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # initialize app with SQLAlchemy instance
    # db.init_app(app)
    # Create database tables given defined models
    with app.app_context():
       db.create_all()
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)