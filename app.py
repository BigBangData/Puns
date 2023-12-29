import os
from datetime import timedelta
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

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
            usr = users(user, "") # leave email blank
            db.session.add(usr) # stage
            # doesn't add automatically because one could rollback
            db.session.commit()
        
        flash(f"Login Successful!", "info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash(f"Already logged in.", "info")
            return redirect(url_for("user"))
        else:
            return render_template('login.html')

@app.route('/user', methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved.", "info")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You're not logged in.", "info")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    flash("You've logged out successfully", "info")
    # clear out user data from session
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
                # why is this showing in login.html not view.html?
                flash(f"User {requested_user} deleted.", "info")
            else:
                flash(f"User {logged_user} not authorized to delete {requested_user}.", "info")
    
    return render_template("view.html", values=users.query.all())

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", name="Admin"))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run

