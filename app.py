import os
import csv
import random
import logging
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

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

# setup flask app
app = Flask(__name__)
# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

# setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwu#$)_@34FmkmKHDF02'
db = SQLAlchemy(app)

# security & login
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# reload user object from user_id stored in session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

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
                flash("Did you signup for an account yet?")
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
    flash("You've logged out.")
    return redirect(url_for('login'))

# view
@app.route('/view', methods=["POST", "GET"])
@login_required
def view():
    csv_file_path = os.path.join('static', 'files', 'puns.csv')
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            puns_list = list(csv_reader)
            # Select a random pun
            random_pun = random.choice(puns_list)
            # Display the question and answer
            question = f"{random_pun['question']}?"
            answer = f"{random_pun['answer']}"
            return render_template('view.html', values=[question, answer])
    except FileNotFoundError:
        logging.error(f"CSV file '{csv_file_path}' not found.")
        return render_template('view.html', values=["An Error Ocurred."])

if __name__ == '__main__':
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # access database
    with app.app_context():
        db.create_all()
    # run app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)