import os
import csv
import spacy
import numpy
import logging

from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
from sqlalchemy.orm import Session

# custom
from db_model import app, db, Answer, Puns
from login import login_bp, start_logs

# register the login blueprint
app.register_blueprint(login_bp)

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
def get_next_pun():
    if 'pun_id' not in session:
        # get the max pun_id for user in answers table
        pun_ids = Answer.query.with_entities(Answer.pun_id)\
            .filter_by(user_id=current_user.id).distinct().all()
        pun_ids = [id[0] for id in pun_ids]
        # check that there are answers for this user before taking max
        logging.info(f"Current pun_ids: {pun_ids}")
        if pun_ids == []:
            max_pun_id = 0
        else:
            # great the first time around, but the second time around the max is the same
            # so it maxes out and goes back to the first pun every time and gets stuck on id=1
            max_pun_id = numpy.max(pun_ids)
            logging.info(f"Else max_pun_id: {max_pun_id}")
        # compute next pun id
        # convert to int because Puns query cannot handle class 'numpy.int32'
        next_pun_id = int(max_pun_id + 1)
        # logging.info(f"Next pun id = {next_pun_id}")
        # Use filter query to get the pun
        # logging.info(f"Type: {type(int(next_pun_id))}")
        pun = Puns.query.filter_by(id=next_pun_id).first()
        # logging.info(f"Pun object from query: {pun}")
        if pun is None:
            logging.info(f"User {current_user.id} maxed out of the puns table")
            # No more puns for the user, start back at first pun
            pun = Puns.query.filter_by(id=1).first()
        # get pun id, question, answer from pun object
        pun_id = pun.id
        question = f"{pun.question}?"
        answer = pun.answer
        # persist for single answer
        session['pun_id'] = pun_id
        session['question'] = question
        session['answer'] = answer
        logging.info(f"{session}")
    else:
        pun_id = session['pun_id']
        question = session['question']
        answer = session['answer']
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
# home
@app.route('/')
def home():
    return render_template('index.html')

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
        # GET method should already have session pun_id, etc. but...
        _, question, _ = get_next_pun()
        return render_template('view.html', values=[question])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    # get session answer
    pun_id, _, answer = get_next_pun()
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
    # start logs
    console_handler = start_logs()
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