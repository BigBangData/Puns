import os
import logging
from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user

# custom
from __init__ import app, db
from db_model import User
from auth import RegisterForm, LoginForm, hash_password, check_password_hash

# define blueprint for login.py
login_bp = Blueprint('login', __name__)

# signup
@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash(f"Username '{form.username.data}' exists. Please try another.", "warning")
                return render_template("signup.html", form=form)
            beta_users = os.environ.get('BETA_USERS')
            if form.username.data not in beta_users:
                flash(f"Username '{form.username.data}' is not valid. Are you an approved beta user?", "warning")
                return render_template("signup.html", form=form)
            hashed_password = hash_password(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            msg = f"Created new account for {form.username.data}. Please login."
            logging.info(msg=msg)
            flash(msg, "info")
            return redirect(url_for('login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", "danger")
            return render_template("signup.html", form=form)
    else:
        try:
            msg = f"You're currently logged in as {current_user.username}. \
                Please log out before signing up with another username."
            flash(msg, "info")
            return redirect(url_for('play'))
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
                if check_password_hash(user_id.password, form.password.data):
                    # clear any session variables related to question and answer
                    session.pop('pun_id', None)
                    session.pop('question', None)
                    session.pop('answer', None)
                    login_user(user_id)
                    flash(f"Hello {user_id.username}, you are logged in.", "info")
                    return redirect(url_for('play'))
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
            return redirect(url_for('play'))
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