import os
import logging
from datetime import datetime
from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user

# custom
from db_model import app, db, User
from auth import bcrypt, RegisterForm, LoginForm

# define blueprint for login.py
login_bp = Blueprint('login', __name__)

# ------
# logging for file and console
def start_logs():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    log_file = os.path.join('logs', f"{datetime.now().strftime('%Y%m%d_%H%M%SMT')}.log")
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    return console_handler

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
                    # clear any session variables related to question and answer
                    session.pop('pun_id', None)
                    session.pop('question', None)
                    session.pop('answer', None)
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