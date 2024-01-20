import logging
import numpy as np
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
# custom imports
from db_model import app, db, Answer, Puns
from login import login_bp, start_logs
from answer import get_md_text_similarity, get_sm_text_similarity, get_st_text_similarity \
    , get_phonetic_fuzzy_similarity, store_answer

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
        logging.info(f"{session}")
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
        # POST: clear session pun data
        session.pop('pun_id', None)
        session.pop('question', None)
        session.pop('answer', None)
        return redirect(url_for('view_answer'))
    else:
        _, question, _ = get_next_pun()
        return render_template('view.html', values=[question])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    """Delivers pun answer and results.
    Uses get_next_pun(), which checks for session data.
    Compares user answer with pun answer given methods; returns scores.
    """
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
            # remove newlines
            user_answer = user_answer.replace('\n', '').replace('\r', '')
            # get score for text comparison using Spacy
            md_t_score = get_md_text_similarity(user_answer, answer)
            sm_t_score = get_sm_text_similarity(user_answer, answer)
            st_t_score = get_st_text_similarity(user_answer, answer)
            p_score = get_phonetic_fuzzy_similarity(user_answer, answer)
            # round score
            md_t_score = float(np.round(md_t_score, 4))
            sm_t_score = float(np.round(sm_t_score, 4))
            st_t_score = float(np.round(st_t_score, 4))
            p_score = float(np.round(p_score, 4))
            # # convert to array
            # t_score_arr = np.array([t_score_4pt])
            # p_score_arr = np.array([p_score_4pt])
            # # calculate mean score
            # mean_score = np.mean([t_score_arr, p_score_arr])
            # store data in answer table
            store_answer(
                user_id=user_id
                , pun_id=pun_id
                , user_answer=user_answer
                , md_txt_sim_score=md_t_score
                , sm_txt_sim_score=sm_t_score
                , st_txt_sim_score=st_t_score
                , phonetic_fuzzy_sim_score=p_score
            )
            # zip data
            data = zip(
                [user_answer, "", "", ""]
                , ['Text (Medium)', 'Text (Small)', 
                   'Sentence (Transf.)', 'Phonetic Fuzzy']
                , [md_t_score, sm_t_score, st_t_score, p_score]
            )
            # return view answer
            return render_template('view_answer.html', values=[answer], data=data)
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
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)