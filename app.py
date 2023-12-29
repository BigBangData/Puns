from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "wjer3498$&_VKA3lkf=="
# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

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

@app.route('/user')
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        flash("You're not logged in.")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    flash("You've logged out successfully", "info")
    # clear out user data from session
    session.pop("user", None)
    return redirect(url_for("login"))

# @app.route('/admin')
# def admin():
#     return redirect(url_for("user", name="Admin!"))

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run

