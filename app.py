import logging
import numpy as np
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
# custom imports
from db_model import app, db, Answer, Puns, Models
from db_insert import insert_into_puns, insert_into_models
from login import login_bp, start_logs
from answer import get_web_sm_similarity, get_web_md_similarity \
    , get_all_st_similarity, get_par_st_similarity \
    , get_phonetic_fuzzy_similarity, get_model_weights \
    , store_answer, store_answer_update

# register the login blueprint
app.register_blueprint(login_bp)

# View
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
        # persist for single answer
        session['pun_id'] = pun_id
        session['question'] = question
        session['answer'] = answer
        #logging.info(f"{session}")
    else:
        pun_id = session['pun_id']
        question = session['question']
        answer = session['answer']
    return pun_id, question, answer


# Routes
# home
@app.route('/')
def home():
    return render_template('index.html')

# view
@app.route('/view', methods=["POST", "GET"])
@login_required
def view():
    """Delivers pun question.
    Uses get_next_pun(), which checks for session data.
    Session pun data is cleared when either:
        1. Users login, or
        2. Users answer a question ("POST" method below)
    """
    if request.method == "POST":
        selected_model = request.form.get('selected_model')
        logging.info(f"selected model: {selected_model}")
        # query models to get the id
        model = Models.query.filter_by(short_name=selected_model).first()
        store_answer_update(
            user_id=current_user.id
            , pun_id=session['pun_id']
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
        return redirect(url_for('view_answer'))
    else:
        _, question, answer = get_next_pun()
        num_words = len(answer.split(" "))
        hint = f"[{num_words} words]"
        return render_template('view.html', values=[question, hint])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    """Delivers pun answer and results.
    Uses get_next_pun(), which checks for session data.
    Compares user answer with pun answer given methods; returns scores.
    """
    # get session answer
    pun_id, question, answer = get_next_pun()
    if request.method == "POST":
        # make sure text area is completed
        user_id = current_user.id
        user_answer = request.form.get('user_answer')

        if not user_answer.strip():
            flash("Text area cannot be empty.", "info")
            return redirect(url_for('view'))
        else:
            # remove newlines
            user_answer = user_answer.replace('\n', '').replace('\r', '')
            # get score for text comparison using Spacy
            score1 = get_web_sm_similarity(user_answer, answer)
            score2 = get_web_md_similarity(user_answer, answer)
            score3 = get_all_st_similarity(user_answer, answer)
            score4 = get_par_st_similarity(user_answer, answer)
            score5 = get_phonetic_fuzzy_similarity(user_answer, answer)
            # gather scores
            scores = [score1, score2, score3, score4, score5]
            rounded_scores = [float(np.round(score, 6)) for score in scores]
            # calculate weighted avg score
            logging.info(f"Model scores: {rounded_scores}")
            weights = get_model_weights()
            logging.info(f"Model weights: {weights}")
            avg_score = np.sum([score * weight for score, weight in zip(scores, weights)])
            avg_score = np.round(avg_score, 6)
            logging.info(f"Weighted Avg. Score: {avg_score}")
            # store data in answer table
            store_answer(
                user_id=user_id
                , pun_id=pun_id
                , user_answer=user_answer
                , scores=rounded_scores
                , avg_score=avg_score
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
            return render_template('view_answer.html', values=values, data=sorted_data)
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
        insert_into_puns()
        insert_into_models()
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)