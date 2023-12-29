from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "wjer3498$&_VKA3lkf=="
# sql database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users/sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFIATIONS'] = False
# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class Users(db.Model):
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
        flash(f"Login Successful!")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash(f"Already logged in.")
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
            flash("Email was saved.")
        else:
            if "email" in session:
                email = session["email"]
        
        return render_template("user.html", email=email)
    else:
        flash("You're not logged in.")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    flash("You've logged out successfully", "info")
    # clear out user data from session
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", name="Admin!"))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run

