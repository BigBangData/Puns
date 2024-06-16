import re
import logging
from flask import redirect, url_for, render_template, flash, request, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

# custom
from __init__ import app, db, logs
from db_model import Puns, Ratings, insert_puns
from login import login_bp

# register the login blueprint
app.register_blueprint(login_bp)

class GetUserRating(FlaskForm):
    """Defines fields for flask forms; used to help avoid CSRF."""
    rating = StringField('Your Answer', render_kw={"rows": 2, "cols": 80, "maxlength": 100})
    submit = SubmitField('VIEW ANSWER', render_kw={"class": "btn-info"})

# Play.html
def get_user_latest_pun_id():
    """Helper function for get_next_pun()"""
    last_play = (
        db.session.query(Ratings)
            .filter_by(user_id=current_user.id)
            .order_by(Ratings.id.desc())
            .first()
    )
    if last_play:
        last_pun_id = last_play.pun_id
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
            latest_pun_id = get_user_latest_pun_id()
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
    form = GetUserRating()
    if request.method == "POST" and form.validate_on_submit():
        # clear session pun data
        session.pop('pun_id', None)
        session.pop('question', None)
        session.pop('answer', None)
        return redirect(url_for('view_answer', form=form))
    else:
        _, question, answer = get_next_pun()
        num_words = len(answer.split(" "))
        num_words_msg = f"[{num_words} words]"
        return render_template('play.html', form=form, values=[question, num_words_msg])

# view asnwer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    """Delivers pun answer and results.
    Uses get_next_pun(), which checks for session data.
    """
    form = GetUserRating()
    # get session rating
    pun_id, question, answer = get_next_pun()
    if request.method == "POST":
        # make sure text area is completed
        user_id = current_user.id
        rating = request.form.get('rating')
        if not rating.strip():
            flash("Text area cannot be empty.", "info")
            return redirect(url_for('play'))
        else:
            # remove newlines and 2+ spaces and html chars
            rating = rating.replace('\n', '').replace('\r', '')
            rating = re.sub(r'\s+', ' ', rating).strip()
            # store known 'play' data in Ratings table
            Ratings.store_ratings(
                user_id=user_id
                , pun_id=pun_id
                , rating=rating
                , avg_user_rating=1 # FINISH LATER
                , avg_pun_rating=2 # FINISH LATER
            )
            # return user answer for ease of comparison
            your_rating = f"Your rating: {rating}"
            values = [question, answer, your_rating]
            # fake data for now
            groan_scale = ['Sigh', 'Eyeroll', 'Groan']
            n_votes = [2, 1, 0]
            data = list(zip(groan_scale, n_votes))
            # return view answer
            return render_template(
                'view_answer.html'
                , values=values
                , data=data
                , form=form
            )
    else:
        return redirect(url_for('play'))

if __name__ == "__main__":
    # start logs
    console_handler = logs()
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # initialize app with SQLAlchemy instance
    # db.init_app(app)
    # Create database tables given defined models
    with app.app_context():
        db.create_all()
        insert_puns()
    # Run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # to run in prod
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)
