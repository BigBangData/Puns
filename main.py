import re
import ast
import random
import logging
import numpy as np
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

# custom
from . import app, db, logs
from .db_model import Answer, Puns, Models
from .db_insert import insert_into_puns, insert_into_models
from .login import login_bp
from .answer import get_web_sm_similarity, get_web_md_similarity \
    , get_phonetic_fuzzy_similarity, get_model_weights \
    , store_answer, store_answer_update

# register the login blueprint
app.register_blueprint(login_bp)

class GetUserAnswer(FlaskForm):
    """Defines fields for flask forms; used to help avoid CSRF.
    """
    user_answer = StringField('Your Answer', render_kw={"rows": 2, "cols": 80, "maxlength": 100})
    submit = SubmitField('VIEW ANSWER', render_kw={"class": "btn-info"})

# threshold for success based on avg_score
THRESH = 0.5

# Play.html
def get_users_latest_answer():
    """Helper function for get_next_pun()"""
    last_answer = (
        db.session.query(Answer)
            .filter_by(user_id=current_user.id)
            .order_by(Answer.id.desc())
            .first()
    )
    if last_answer:
        last_pun_id = last_answer.pun_id
        logging.info(f"User {current_user} - lastest pun id {last_pun_id}")
    else:
        logging.info(f"No answers found for user: {current_user}.")
        last_pun_id = 0
    # return last pun_id
    return last_pun_id

def get_next_pun():
    """Gets the next pun."""
    if 'pun_id' not in session:
        # get users' latest pun_id
        # 0 if user hasn't answered yet
        if current_user.is_authenticated:
            latest_pun_id = get_users_latest_answer()
        else:
            latest_pun_id = 0
        # get next pun
        next_pun_id = latest_pun_id + 1
        logging.info(f"Next pun id: {next_pun_id}")
        # use filter query to get the pun row
        pun = Puns.query.filter_by(id=next_pun_id).first()
        logging.info(f"Pun object: {pun}")
        # None when next pun_id isn't in the puns table
        if pun is None:
            logging.info(f"User {current_user} answered all puns.")
            # No more puns for the user, start back at first pun
            pun = Puns.query.filter_by(id=1).first()
        # get pun id, question, answer from pun object
        pun_id = pun.id
        question = f"{pun.question}?"
        answer = pun.answer
        hint = pun.hint
        # persist for single answer
        session['pun_id'] = pun_id
        session['question'] = question
        session['answer'] = answer
        session['hint'] = hint
        #logging.info(f"{session}")
    else:
        pun_id = session['pun_id']
        question = session['question']
        answer = session['answer']
        hint = session['hint']
    return pun_id, question, answer, hint

def select_best_model():
        # given feedback
        feedback = request.form.get("feedback")
        logging.info(f"Received feedback: {feedback}")
        # given last answer's avg score
        last_answer = (
            db.session.query(Answer)
                .filter_by(user_id=current_user.id)
                .order_by(Answer.id.desc())
                .first()
        )
        # calculate whether user guessed correctly, given the same threshold
        correct_guess = last_answer.avg_score > THRESH
        logging.info(f"Guessed correctly? {correct_guess}")
        # get max / min scores
        scores_list = ast.literal_eval(last_answer.scores)
        scores_array = np.array(scores_list)
        logging.info(f"Scores array: {scores_array}")
        max_score = np.max(scores_array)
        min_score = np.min(scores_array)
        logging.info(f"Max score: {max_score}; Min score: {min_score}")
        # select best model given feedback and guess
        # first need to get the best model ID given the score and a "max" or "min" goal
        def get_best_ix_given_score(score, max_or_min):
            # helper function to get model ix for best / worst scores
            # account for possibility of more than one model having the max or min score
            logging.info(f"{max_or_min} score: {score}")
            ix_list = [ix for ix, s in enumerate(scores_array) if s == score]
            logging.info(f"List of model(s) that match the {max_or_min} score: {ix_list}")
            # chose randomly out of candidates
            random_ix = random.randint(0, len(ix_list)-1)
            logging.info(f"Random index chosen: {random_ix}")
            # adjust index from python zero-base to database one-base numbering
            best_model_ix = ix_list[random_ix] +1
            logging.info(f"Best model index: {best_model_ix}")
            return best_model_ix
        # model with highest match score performed best IF...
        # it was deemed a correct guess and the feedback confirmed it with AGREE OR
        # it was deemed an incorrect guess but the feedback disconfirmed it with DISAGREE
        if correct_guess and feedback == 'AGREE' or not correct_guess and feedback == 'DISAGREE':
            # get ix for model with best or worst score
            best_model_ix = get_best_ix_given_score(max_score, 'max')
        # ELSE the model with lowest match score performed best because...
        # it was deemed an incorrect guess and the feedback confirmed it with AGREE OR
        # it was deemed a correct guess and the feedback disconfirmed it with DISAGREE
        else:
            # get ix for model with worst score
            best_model_ix = get_best_ix_given_score(min_score, 'min')
        return feedback, best_model_ix

def run_app():
    # start logs
    console_handler = logs()
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # initialize app with SQLAlchemy instance
    # db.init_app(app)
    # Create database tables given defined models
    with app.app_context():
        db.create_all()
        insert_into_puns()
        insert_into_models()
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)


# Routes
# home
@app.route('/')
def home():
    return render_template('index.html')

# play
@app.route('/play', methods=["POST", "GET"])
@login_required
def play():
    """Delivers pun question.
    Uses get_next_pun(), which checks for session data.
    Session pun data is cleared when either:
        1. Users login, or
        2. Users answer a question ("POST" method below)
    """
    form = GetUserAnswer()
    if request.method == "POST" and form.validate_on_submit():
        # get best model given feedback and guess
        feedback, best_model_ix = select_best_model()
        # query models to get the id
        model = Models.query.filter_by(id=best_model_ix).first()
        store_answer_update(
            user_id=current_user.id
            , pun_id=session['pun_id']
            , user_confirmed_as=feedback
            , selected_model=model.id
        )
        # increment the num_votes in models
        model.num_votes += 1
        db.session.commit()
        # calculate the weighted_avg: model.num_votes / sum_votes
        # clear session pun data
        session.pop('pun_id', None)
        session.pop('question', None)
        session.pop('answer', None)
        return redirect(url_for('view_answer', form=form))
    else:
        _, question, answer, hint = get_next_pun()
        num_words = len(answer.split(" "))
        num_words_msg = f"[{num_words} words]"
        return render_template('play.html', form=form, values=[question, num_words_msg, hint])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    """Delivers pun answer and results.
    Uses get_next_pun(), which checks for session data.
    Compares user answer with pun answer given methods; returns scores.
    """
    form = GetUserAnswer()
    # get session answer
    pun_id, question, answer, _ = get_next_pun()
    if request.method == "POST":
        # make sure text area is completed
        user_id = current_user.id
        user_answer = request.form.get('user_answer')
        if not user_answer.strip():
            flash("Text area cannot be empty.", "info")
            return redirect(url_for('play'))
        else:
            # remove newlines and 2+ spaces and html chars
            user_answer = user_answer.replace('\n', '').replace('\r', '')
            user_answer = re.sub(r'\s+', ' ', user_answer).strip()
            # get score for text comparison using Spacy
            score1 = get_web_sm_similarity(user_answer, answer)
            score2 = get_web_md_similarity(user_answer, answer)
            score3 = get_phonetic_fuzzy_similarity(user_answer, answer)
            # gather scores
            scores = [score1, score2, score3]
            rounded_scores = [float(np.round(score, 6)) for score in scores]
            # calculate weighted avg score
            logging.info(f"Model scores: {rounded_scores}")
            weights = get_model_weights()
            logging.info(f"Model weights: {weights}")
            avg_score = np.sum([score * weight for score, weight in zip(scores, weights)])
            avg_score = np.round(avg_score, 6)
            logging.info(f"Weighted Avg. Score: {avg_score}")
            # add Boolean int for correct guess to be passed to Javascript frontend for effects
            correct_guess = int(avg_score > THRESH)
            # store known 'play' data in answer table
            store_answer(
                user_id=user_id
                , pun_id=pun_id
                , user_answer=user_answer
                , scores=rounded_scores
                , avg_score=avg_score
                , correct_guess=correct_guess
                , user_confirmed_as=None
                , selected_model=None
            )
            # query all the short_name values from the Models table
            names = Models.query.with_entities(Models.short_name).all()
            # convert the result to a list
            model_names = [name[0] for name in names]
            # gather data
            data = list(zip(model_names, rounded_scores))
            # sort on scores desc.
            sorted_data = sorted(data, key=lambda x: x[1], reverse=True)
            # append average score
            average_score_row = ("Weighted Avg. Score:", avg_score)
            sorted_data.append(average_score_row)
            # return user answer for ease of comparison
            your_answer = f"Your Answer: {user_answer}"
            values = [question, answer, your_answer]
            # return view answer
            return render_template(
                'view_answer.html'
                , values=values
                , data=sorted_data
                , correct_guess=correct_guess
                , form=form
            )
    else:
        return redirect(url_for('play'))
