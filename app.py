import os
import csv
import spacy
import numpy
import logging

from datetime import datetime
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_user, login_required, logout_user, current_user


# custom
from db_model import app, db, User, Answer, Puns
from auth import bcrypt, RegisterForm, LoginForm

# logging for file and console
if not os.path.exists('logs'):
    os.makedirs('logs')
log_file = os.path.join('logs', f"{datetime.now().strftime('%Y%m%d_%H%M%SMT')}.log")
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(log_format)
console_handler.setFormatter(formatter)

# load data from CSV and populate the puns table
def populate_puns():
    try:
        csv_path = os.path.join('static', 'files', 'puns.csv')
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                new_pun = Puns(question=row['question'], answer=row['answer'])
                db.session.add(new_pun)
        db.session.commit()
    except FileNotFoundError:
        logging.error(f"CSV file '{csv_path}' not found.")

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

def store_answer(user_id, pun_id, user_answer, score):
    new_answer = Answer(
        user_id=user_id
        , pun_id=pun_id
        , user_answer=user_answer
        , score=score
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()

# View
def get_pun():
    if 'pun_id' not in session:
        # get the max pun_id for user in answers table
        pun_ids = Answer.query.with_entities(Answer.pun_id)\
            .filter_by(user_id=current_user.id).distinct().all()
        pun_ids = [id[0] for id in pun_ids]
        # check that there are answers for this user before taking max
        if pun_ids == []:
            max_pun_id = 0
        else:
            max_pun_id = numpy.max(pun_ids)
        # compute next pun id
        next_pun_id = max_pun_id + 1
        logging.info(f"Next pun id = {next_pun_id}")
        # why does this fail on the 2nd ID?
        pun = Puns.query.get(next_pun_id)
        logging.info(f"Pun object from query: {pun}")
        # this fails on the second time because None has no attribute id
        pun_id = pun.id
        question = f"{pun.question}?"
        answer = pun.answer
        # add to session to persist specific pair
        session['pun_id'] = pun_id
        session['question'] = question
        session['answer'] = answer
        logging.info(f"{session}")
    else:
        pun_id = session['pun_id']
        question = session['question']
        answer = session['answer']
    # return new ones or same ones if already in session
    return pun_id, question, answer

# View Answer
def get_reaction_message(score):
    if score >= 0.8:
        return "Punbelievable, you're on fire!"
    elif 0.6 <= score < 0.8:
        return "Punderful job."
    else:
        return "Hm, that wasn't puntastic."

# Routes
# ------
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

# view
@app.route('/view', methods=["POST", "GET"])
@login_required
def view():
    if request.method == "POST":
        # clear session variables related to question and answer
        session.pop('pun_id', None)
        session.pop('question', None)
        session.pop('answer', None)
        return redirect(url_for('view_answer'))
    else:
        _, question, _ = get_pun()
        return render_template('view.html', values=[question])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    # get session answer
    pun_id, _, answer = get_pun()
    if request.method == "POST":
        # make sure text area is completed
        user_id = current_user.id
        user_answer = request.form.get('user_answer')
        if not user_answer.strip():
            flash("Text area cannot be empty.", "info")
            return redirect(url_for('view'))
        else:
            # get score for text comparison
            score = compare_texts(user_answer, answer)
            # store data in answer table
            store_answer(
                user_id=user_id
                , pun_id=pun_id
                , user_answer=user_answer
                , score=score
            )
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
       populate_puns()
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)