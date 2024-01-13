import logging
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
# custom imports
from db_model import app, db, Answer, Puns
from login import login_bp, start_logs
from answer import compare_answer_similarity, store_answer

# register the login blueprint
app.register_blueprint(login_bp)

# View
def get_users_latest_answer():
    """Helper function for get_next_pun()"""
    latest_answer = (
        db.session.query(Answer)
            .filter_by(user_id=current_user.id)
            .order_by(Answer.id.desc())
            .first()
    )
    if latest_answer:
        latest_pun_id = latest_answer.pun_id
        logging.info(f"latest_pun_id: {latest_pun_id}")
    else:
        logging.info(f"No answers found for {current_user.id}.")
        latest_pun_id = 0
    return latest_pun_id

def get_next_pun():
    """Gets the next pun."""
    if 'pun_id' not in session:
        # get users' latest pun_id
        # 0 if user hasn't answered yet
        latest_pun_id = get_users_latest_answer()
        # get next pun
        next_pun_id = latest_pun_id + 1
        logging.info(f"next_pun_id: {next_pun_id}")
        # use filter query to get the pun row
        pun = Puns.query.filter_by(id=next_pun_id).first()
        logging.info(f"Pun object id: {pun}")
        # None when next pun_id isn't in the puns table
        if pun is None:
            logging.info(f"User {current_user.id} answered all puns.")
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
            score = compare_answer_similarity(user_answer, answer)
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
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)