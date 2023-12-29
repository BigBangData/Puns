import os
import logging
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

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

# setup db
abspath = os.path.abspath(os.path.dirname(__file__))
sqlite_path = 'sqlite:///' + os.path.join(abspath, 'app.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route('/')
def home():
    # return render_template('index.html', content=['Mary', 'Joe', 'Anna'])
    return render_template('index.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        # if user exists
        # find all users with this name, grab first
        # assumes names are unique, coult try .all() or .delete()
        # could loop through objects if using .all() to delete them
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            # if user exists, grab email for session
            session["email"] = found_user.email
        else:
            msg = f"Creating user {user} in database."
            logging.info(msg=msg)
            usr = users(user, "") # leave email blank
            db.session.add(usr) # stage
            # doesn't add automatically because one could rollback
            db.session.commit()
        # display message
        msg = f"{user}, you are logged in."
        flash(msg, "info")
        logging.info(msg=msg)
        return redirect(url_for("user"))
    else:
        if "user" in session:
            logged_user = session["user"]
            msg = f"{logged_user}, you are already logged in."
            flash(msg, "info")
            logging.info(msg=msg)
            return redirect(url_for("user"))
        else:
            return render_template('login.html')

@app.route('/user', methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        logged_user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=logged_user).first()
            found_user.email = email
            db.session.commit()
            msg = f"{logged_user}, your email {email} was saved."
            flash(msg, "info")
            logging.info(msg=msg)
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        msg = f"{user}, you are already logged in."
        flash(msg, "info")
        logging.info(msg=msg)
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "user" in session:
        logged_user = session["user"]
        msg = f"{logged_user}, you have logged out successfully."
        flash(msg, "info")
        logging.info(msg=msg)
        session.pop("user", None)
        session.pop("email", None)
        return redirect(url_for("login"))
    else:
        msg = "You are not logged in."
        flash(msg, "info")
        logging.info(msg=msg)
        session.pop("user", None)
        session.pop("email", None)
        return redirect(url_for("login"))

@app.route('/view', methods=["POST", "GET"])
def view():
    # only user can delete their data
    if "user" in session:
        logged_user = session["user"]
        if request.method == "POST":
            requested_user = request.form["user"]
            if logged_user == requested_user:
                users.query.filter_by(name=logged_user).delete()
                db.session.commit()
                msg = f"{logged_user} successfully deleted."
                flash(msg, "info")
                logging.info(msg=msg)
                # since we can have multiple users with the same name
                same_name_users = users.query.filter_by(name=logged_user).all()
                return render_template("view.html", values=same_name_users)
            else:
                ui_msg = f"User  {logged_user} not authorized to delete requested user."
                console_msg = f"User {logged_user} not authorized to delete {requested_user}."
                flash(ui_msg, "info")
                logging.info(msg=console_msg)
                same_name_users = users.query.filter_by(name=logged_user).all()
                return render_template("view.html", values=same_name_users)
        elif request.method == "GET":
            same_name_users = users.query.filter_by(name=logged_user).all()
            return render_template("view.html", values=same_name_users)
        else:
            pass
    else:
        flash(f"Please log in to view and manage user data.", "info")
        return redirect(url_for("login"))

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", name="admin"))

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