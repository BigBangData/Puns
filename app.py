import os
import logging
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError

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
app.secret_key = "wjer3498$&_VKA3lkf=="
# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

# setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'qwu#$)_@34FmkmKHDF02'
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=8, max=20)]
        , render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)]
        , render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            msg = 'Username already exists. Please try another.'
            raise ValidationError(msg)

class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=8, max=20)]
        , render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)]
        , render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('index.html')

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # start session
        session.permanent = True
        # get username
        username = request.form["username"]
        session["username"] = username
        # check if user already exists
        # if so, redirect to login
        found_user = User.query.filter_by(username=username).first()
        if found_user:
            msg = f"{username}, you already have an account. Please login." # check if logged in already
            flash(msg, "info")
            logging.info(msg=msg)
            return redirect(url_for("login")) # gets two messages if already logged in
        else:
            # create an account
            internal_msg = f"Creating user {username} in database."
            logging.info(msg=internal_msg)
            usr = User(username, "")
            db.session.add(usr) # stage
            # doesn't add automatically because one could rollback
            db.session.commit()
            # message user
            msg = f"Created account for {username}."
            logging.info(msg=msg)
            usr = User(username, "")
            return redirect(url_for("login")) # gets two messages if already logged in
    # "GET" method
    else:
        return render_template('register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # start session
        session.permanent = True
        # get username
        username = request.form["username"]
        session["username"] = username
        # check if user already exists
        # find all users with this name, grab first
        # assumes names are unique, coult try .all() or .delete()
        # could loop through objects if using .all() to delete them
        found_user = User.query.filter_by(username=username).first()
        if found_user:
            # if user exists, grab password for session
            session["password"] = found_user.password
            # authenticate first
            msg = f"{username}, you are logged in."
            flash(msg, "info")
            logging.info(msg=msg)
            return redirect(url_for("view"))
        else:
            # redirect to register
            msg = f"User {username} not found. Please register for an account."
            logging.info(msg=msg)
            flash(msg, "info")
            return redirect(url_for("register"))
    # "GET" method
    else:
        if "username" in session:
            logged_user = session["username"]
            msg = f"{logged_user}, you are already logged in."
            flash(msg, "info")
            logging.info(msg=msg)
            return redirect(url_for("view"))
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    if "username" in session:
        logged_user = session["username"]
        msg = f"{logged_user}, you have logged out successfully."
        flash(msg, "info")
        logging.info(msg=msg)
        session.pop("username", None)
        session.pop("password", None)
        return redirect(url_for("login"))
    else:
        msg = "You are not logged in."
        flash(msg, "info")
        logging.info(msg=msg)
        return redirect(url_for("login"))

@app.route('/view', methods=["POST", "GET"])
def view():
    # only user can delete their data
    if "username" in session:
        logged_user = session["username"]
        if request.method == "POST":
            requested_user = request.form["username"]
            if logged_user == requested_user:
                # permission to delete its own data
                User.query.filter_by(username=logged_user).delete()
                db.session.commit()
                msg = f"{logged_user} successfully deleted."
                flash(msg, "info")
                logging.info(msg=msg)
                # user filter
                # user_filter = User.query.filter_by(username=logged_user).all()
                # revamped permission to view all users
                admin_filter = User.query.all()
                return render_template("view.html", values=admin_filter)
            else:
                ui_msg = f"User {logged_user} not authorized to delete requested user."
                console_msg = f"User {logged_user} not authorized to delete {requested_user}."
                flash(ui_msg, "info")
                logging.info(msg=console_msg)
                admin_filter = User.query.all()
                return render_template("view.html", values=admin_filter)
        # "GET" method
        else:
            admin_filter = User.query.all()
            return render_template("view.html", values=admin_filter)
    else:
        flash(f"Please log in to view and manage user data.", "info")
        return redirect(url_for("login"))

if __name__ == '__main__':
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # access db
    with app.app_context():
        db.create_all()
    # run app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)