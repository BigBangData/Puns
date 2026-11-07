import io
import os
import csv
import base64
import logging
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

## Initial Setup

# setup flask app
app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)

@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    return render_template('csrf_error.html'), 400

# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

# setup database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# uncomment for creating new database from scratch
if 'sqlalchemy' in app.extensions:
    del app.extensions['sqlalchemy']

# instantiate database
db = SQLAlchemy(app)

# logging for file and console
def logs():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    log_file = os.path.join('logs', f"{datetime.now().strftime('%Y%m%d_%H%M%SMT')}.log")
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    return console_handler

# Define Database Schema

# table models
class User(db.Model, UserMixin):
    """Dynamic: filled as users signup"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    # define relationship to the "Ratings" table
    ratings = db.relationship('Ratings', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Puns(db.Model):
    """Static: filled by insert_into_puns()"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    blame = db.Column(db.String(255), nullable=True)
    # define relationship to the "Ratings" table
    ratings = db.relationship('Ratings', backref='puns', lazy=True)

def insert_puns():
    try:
        existing_records = Puns.query.first()
        if existing_records is None:
            csv_path = os.path.join('static', 'files', 'puns.csv')
            with open(csv_path, mode='r', encoding='utf-8-sig') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                row_count = 0
                for row in csv_reader:
                    new_pun = Puns(
                        question=row['question']
                        , answer=row['answer']
                        , blame=row['blame']
                    )
                    db.session.add(new_pun)
                    row_count += 1
                logging.info(f"Inserted {row_count} rows into Puns.")
            db.session.commit()
        else:
            logging.info("Skipped Insert - table Puns already exists.")
    except FileNotFoundError:
        logging.error(f"CSV file '{csv_path}' not found.")

class Ratings(db.Model):
    """Dynamic: filled as users rate puns"""
    id = db.Column(db.Integer, primary_key=True)
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pun_id = db.Column(db.Integer, db.ForeignKey('puns.id'), nullable=False)
    # user rating on a 1-3 scale for a given pun
    rating = db.Column(db.String, nullable=False)

    def __init__(self, user_id, pun_id, rating):
        self.user_id = user_id
        self.pun_id = pun_id
        self.rating = rating

    def store_ratings(user_id: int, pun_id: int, rating: str):
        new_rating = Ratings(user_id=user_id, pun_id=pun_id, rating=rating)
        current_user.ratings.append(new_rating)
        db.session.add(new_rating)
        db.session.commit()

class UserProgress(db.Model):
    """Tracks ordered-game progress independently from ratings on selected puns."""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    pun_id = db.Column(db.Integer, nullable=False, default=0)

## Authentication for Signup and Login

# security
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# functions for hashing and checking passwords
def hash_password(password):
    return ph.hash(password)

def check_password_hash(hashed_password, plain_password):
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

# reload user object from user_id stored in session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Username is required."),
            Length(min=4, max=20, message="Username must be between 4 and 20 characters.")
        ],
        render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),
            Length(min=8, max=20, message="Password must be between 8 and 20 characters.")
        ],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Signup")

    def validate_username(self, username):
        if len(username.data) < 4 or len(username.data) > 20:
            return  # Skip checking existing user if length is invalid

        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("User exists.")

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Username is required."),
            Length(min=4, max=20, message="Username must be between 4 and 20 characters.")
        ],
        render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Password is required."),
            Length(min=8, max=20, message="Password must be between 8 and 20 characters.")
        ],
        render_kw={"placeholder": "Password"}
    )
    submit = SubmitField("Login")


## Define Routes

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Signup
@app.route("/signup", methods=["POST", "GET"])
def signup():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash(f"Username '{form.username.data}' exists. Please try another.", "warning")
                return render_template("signup.html", form=form)
            try:
                beta_users = os.getenv('BETA_USERS').split(',')
            except AttributeError as e:
                logging.debug(F"AttributeError: {e}")
                flash(f"An error ocurred.", "warning")
            if form.username.data not in beta_users:
                flash(f"Username '{form.username.data}' is not valid. Are you an approved beta user?", "warning")
                return render_template("signup.html", form=form)
            else:
                hashed_password = hash_password(form.password.data)
                new_user = User(username=form.username.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                msg = f"Created new account for {form.username.data}. Please login."
                logging.info(msg=msg)
                flash(msg, "info")
                return redirect(url_for('login'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Error in {getattr(form, field).label.text}: {error}", "danger")
            return render_template("signup.html", form=form)
    else:
        try:
            msg = f"You're currently logged in as {current_user.username}. \
                Please log out before signing up with another username."
            flash(msg, "info")
            return redirect(url_for('play'))
        # throws error when current_user is Anonymous (not logged in)
        except AttributeError:
            return render_template('signup.html', form=form)

# Login
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user_id = User.query.filter_by(username=form.username.data).first()
            if user_id:
                if check_password_hash(user_id.password, form.password.data):
                    # clear any session variables related to question and answer
                    session.pop('pun_id', None)
                    session.pop('question', None)
                    session.pop('answer', None)
                    session.pop('start_new_game', None)
                    session.pop('pun_selection_mode', None)
                    login_user(user_id)
                    flash(f"Hello {user_id.username}, you are logged in.", "info")
                    return redirect(url_for('play'))
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
            return redirect(url_for('play'))
        # throws error when current_user = AnonymousUserMixin
        except AttributeError:
            return render_template('login.html', form=form)

# Logout
@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash("You've logged out.", "info")
    return redirect(url_for('login'))

# Helper funcs for Play
def get_user_latest_pun_id():
    """Return ordered progress, initializing it from pre-existing ratings once."""
    progress = UserProgress.query.filter_by(user_id=current_user.id).first()
    if progress is None:
        last_rating = (
            db.session.query(Ratings)
                .filter_by(user_id=current_user.id)
                .order_by(Ratings.id.desc())
                .first()
        )
        last_pun_id = last_rating.pun_id if last_rating else 0
        progress = UserProgress(user_id=current_user.id, pun_id=last_pun_id)
        db.session.add(progress)
        db.session.commit()
        logging.info(f"Initialized ordered progress for {current_user}: {last_pun_id}")
    return progress.pun_id

def set_user_latest_pun_id(pun_id):
    """Update ordered progress after rating a pun in the ordered game."""
    progress = UserProgress.query.filter_by(user_id=current_user.id).first()
    if progress is None:
        get_user_latest_pun_id()
        progress = UserProgress.query.filter_by(user_id=current_user.id).first()
    progress.pun_id = pun_id
    db.session.commit()

def get_pun_progress():
    """Return rounded progress and the pun IDs completed in the current run."""
    pun_ids = [
        pun_id for (pun_id,) in db.session.query(Puns.id).order_by(Puns.id).all()
    ]
    pun_total = len(pun_ids)
    latest_pun_id = get_user_latest_pun_id()
    if pun_ids and latest_pun_id >= pun_ids[-1]:
        completed_pun_ids = []
    else:
        completed_pun_ids = [
            pun_id for pun_id in pun_ids if pun_id <= latest_pun_id
        ]
    percentage = round(len(completed_pun_ids) / pun_total * 100) if pun_total else 0
    return percentage, pun_ids, completed_pun_ids

def get_next_pun():
    """Gets the next pun."""
    if 'pun_id' not in session:
        # get users' latest pun_id
        # 0 if user hasn't answered yet
        if session.pop('start_new_game', False):
            latest_pun_id = 0
        elif current_user.is_authenticated:
            latest_pun_id = get_user_latest_pun_id()
        else:
            latest_pun_id = 0
        # get next pun
        next_pun_id = latest_pun_id + 1
        logging.info(f"Next pun id: {next_pun_id}")
        # use filter query to get the pun row
        pun = Puns.query.filter_by(id=next_pun_id).first()
        # 'None' when next pun_id isn't in the puns table
        if pun is None:
            logging.info(f"User {current_user} answered all puns.")
            # No more puns for the user, start back at first pun
            pun = Puns.query.filter_by(id=1).first()
        # get pun id, question, answer from pun object
        pun_id = pun.id
        question = f"{pun.question}?"
        answer = pun.answer
        blame = pun.blame
        # persist for single answer
        session['pun_id'] = pun_id
        session['question'] = question
        session['answer'] = answer
        session['blame'] = blame
        #logging.info(f"{session}")
    else:
        pun_id = session['pun_id']
        question = session['question']
        answer = session['answer']
        blame = session['blame']
    return pun_id, question, answer, blame

pun_factor_dict = {
    'no': '\U0001F636',
    'wut': '\U0001F9D0',
    'sigh': '\U0001F624',
    'eyeroll': '\U0001F644',
    'groan': '\U0001F62C',
    'panic': '\U0001FAE8'
}

CONFETTI_MIN_GAP = 2
CONFETTI_MAX_GAP = 10
CONFETTI_GAP_WEIGHTS = (4, 2, 3, 4, 3, 2, 1, 1, 1)
CONFETTI_SEED = 2025

animal_dict = {
    'dragon': [],
    'unicorn': [],
    'owl': [],
    'zebra': [],
    'ladybug': [],
    'jellyfish': [],
    'axolotl': []
}


def build_confetti_schedule(max_total_votes):
    """Build a deterministic, repeating confetti schedule with guardrails.

    The schedule stays stable across refreshes by using a fixed seed, while still
    varying the gap lengths and animal choices enough to feel unpredictable.
    """
    if max_total_votes is None:
        max_total_votes = 0
    max_total_votes = max(int(max_total_votes), 0)

    schedule = {}
    rng = random.Random(CONFETTI_SEED)
    next_vote = 0
    previous_animal = None

    while next_vote <= max_total_votes:
        gap = rng.choices(
            range(CONFETTI_MIN_GAP, CONFETTI_MAX_GAP + 1),
            weights=CONFETTI_GAP_WEIGHTS,
            k=1
        )[0]
        next_vote += gap
        animal_pool = list(animal_dict.keys())
        if previous_animal is not None:
            animal_pool = [animal for animal in animal_pool if animal != previous_animal]
        animal = rng.choice(animal_pool)
        schedule[next_vote] = animal
        previous_animal = animal

    return schedule


# throw confetti given tot_votes which is actual votes (clicks) not based on pun_id
def get_confetti_go_list(tot_votes, animal_dict):
    tot_votes = max(int(tot_votes), 0)
    schedule = build_confetti_schedule(tot_votes)
    active_animal = schedule.get(tot_votes)

    return [
        1 if active_animal == animal else 0
        for animal in animal_dict.keys()
    ]

def query_voting_stats():
    # query Ratings and count user selections
    vote_counts = db.session.query(
        Ratings.user_id,
        Ratings.rating,
        db.func.count(Ratings.rating)
    ).filter_by(user_id=current_user.id).group_by(Ratings.user_id, Ratings.rating).all()
    # create a dictionary to hold the counts
    vote_count_dict = {rating: count for _, rating, count in vote_counts}
    # list panic scale and ratings array
    panic_scale = list(pun_factor_dict.keys())
    panic_scale_rating = np.array([1, 2, 3, 4, 5, 6])
    # create a votes_list by mapping the actual counts to the possible ratings
    # default to 0 if not mapped
    votes_list = [vote_count_dict.get(deg, 0) for deg in panic_scale]
    # combine the panic scale and votes_list into data to be passed to view_answer
    data = list(zip(panic_scale, votes_list, panic_scale_rating))
    return data

# Play
@app.route('/play', methods=["POST", "GET"])
@login_required
def play():
    """Delivers pun question.
    Uses get_next_pun(), which checks for session data.
    Session pun data is cleared when either:
        1. Users login, or
        2. Users answer a question ("POST" method below)
    """
    if request.method == "POST":
        if 'pun_id' not in session:
            return redirect(url_for('play'))
        # get rating
        rating = request.form.get("feedback")
        logging.info(f"Received rating: {rating}")
        # get current session data
        pun_id, question, answer, _ = get_next_pun()
        user_id = current_user.id
        # store known 'rating' data in Ratings table
        Ratings.store_ratings(
            user_id=user_id
            , pun_id=pun_id
            , rating=rating
        )
        if session.get('pun_selection_mode') != 'random':
            set_user_latest_pun_id(pun_id)
        session.pop('pun_selection_mode', None)
        # clear session pun data
        session.pop('pun_id', None)
        session.pop('question', None)
        session.pop('answer', None)
        session.pop('blame', None)
        # reload page for GET method
        return redirect(url_for('play'))
    else:
        pun_total = Puns.query.count()
        latest_pun_id = get_user_latest_pun_id()
        if (
            'pun_id' not in session
            and not session.get('start_new_game')
            and (latest_pun_id == 0 or latest_pun_id >= pun_total)
        ):
            progress_percent, pun_ids, completed_pun_ids = get_pun_progress()
            return render_template(
                'play.html',
                intro=True,
                finished=latest_pun_id >= pun_total and latest_pun_id > 0,
                progress_percent=progress_percent,
                pun_ids=pun_ids,
                completed_pun_ids=completed_pun_ids,
                current_pun_id=None
            )

        # GET: get next pun question and answer
        _, question, answer, blame = get_next_pun()
        num_words = len(answer.split(" "))
        if num_words == 1:
            num_words_msg = f"[{num_words} word]"
        else:
            num_words_msg = f"[{num_words} words]"
        # query voting stats
        data = query_voting_stats()
        # unpack votest list
        votes_list = [item[1] for item in data]
        # sum votes
        tot_votes = np.sum(votes_list)
        # get go nogo for each animal
        go_list = get_confetti_go_list(tot_votes=tot_votes, animal_dict=animal_dict)
        drag_go, unic_go, owls_go, zebr_go, lady_go, jell_go, axol_go = go_list
        progress_percent, pun_ids, completed_pun_ids = get_pun_progress()
        # return play
        return render_template(
            'play.html'
            , values=[question, num_words_msg]
            , dragons_go=drag_go
            , unicorns_go=unic_go
            , owls_go=owls_go
            , zebras_go=zebr_go
            , ladybugs_go=lady_go
            , jellyfishes_go=jell_go
            , axolotls_go=axol_go
            , intro=False
            , progress_percent=progress_percent
            , pun_ids=pun_ids
            , completed_pun_ids=completed_pun_ids
            , current_pun_id=session.get('pun_id')
        )

# Select a pun directly from the progress grid or number picker.
@app.route('/jump', methods=["POST"])
@login_required
def jump_to_pun():
    pun_id = request.form.get("pun_id", type=int)
    if pun_id is None:
        pun_id = request.form.get("pun_number", type=int)
    pun = Puns.query.filter_by(id=pun_id).first() if pun_id is not None else None
    if pun is None:
        flash("Please choose an available pun number.", "warning")
        return redirect(url_for('play'))

    for key in ('pun_id', 'question', 'answer', 'blame', 'start_new_game'):
        session.pop(key, None)
    session['pun_id'] = pun.id
    session['question'] = f"{pun.question}?"
    session['answer'] = pun.answer
    session['blame'] = pun.blame
    session['pun_selection_mode'] = 'random'
    return redirect(url_for('play'))

# Start or restart a run after the intro screen.
@app.route('/start', methods=["POST"])
@login_required
def start_game():
    pun_total = Puns.query.count()
    latest_pun_id = get_user_latest_pun_id()
    if latest_pun_id not in (0, pun_total):
        return redirect(url_for('play'))

    for key in ('pun_id', 'question', 'answer', 'blame', 'pun_selection_mode'):
        session.pop(key, None)
    session['start_new_game'] = True
    return redirect(url_for('play'))

# View Answer
@app.route('/view_answer', methods=["POST", "GET"])
@login_required
def view_answer():
    """Delivers pun answer and results.
    Uses get_next_pun(), which checks for session data.
    """
    if request.method == "POST":
        if 'pun_id' not in session:
            return redirect(url_for('play'))
        # get session data
        _, question, answer, blame = get_next_pun()
        if blame:
            blame = f"~ blame {blame}"
        values = [question, answer, blame]
        progress_percent, pun_ids, completed_pun_ids = get_pun_progress()
        # return view answer
        return render_template(
            'view_answer.html'
            , values=values
            , pun_factor_dict=pun_factor_dict
            , progress_percent=progress_percent
            , pun_ids=pun_ids
            , completed_pun_ids=completed_pun_ids
            , current_pun_id=session.get('pun_id')
        )
    else:
        return redirect(url_for('play'))

# Stats
@app.route('/stats', methods=["GET"])
@login_required
def stats():
    """Display user-level stats (for now)."""
    # query voting stats
    data = query_voting_stats()

    # extract data for the plot
    scales = [item[0] for item in data]
    votes = [item[1] for item in data]
    rating_scale = [item[2] for item in data]

    # get total votes
    tot_votes = np.sum(votes)

    # calculate avg rating across votes
    ratings_array = rating_scale * np.array(votes)
    avg_rating = np.sum(ratings_array) / tot_votes

    # ensure 0 instead of nan for first calculation
    if np.isnan(avg_rating):
       avg_rating = 0

    # create a simple bar plot with custom size and background color
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#4e505b')
    ax.set_facecolor('#4e505b')

    bar_width = 0.95
    ax.bar(scales, votes, color='#629cd5', width=bar_width)

    ax.set_ylabel('Num Votes', color='white')
    ax.set_title('Your Ratings', color='white')

    # set color for tick labels
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # ensure y-axis has integer ticks
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # add vertical dashed red line for avg rating
    avg_rating_x = avg_rating - 1
    ax.axvline(avg_rating_x, color='#b34a4a', linestyle='--', linewidth=3, label=f'Avg rating: {avg_rating:.2f}')
    ax.legend(facecolor='white', edgecolor='white', labelcolor='#2c2c2c', title=f'# Votes: {tot_votes}')

    # save the plot to a string buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('stats.html', img_data=img_data)


if __name__ == "__main__":
    # start logs
    console_handler = logs()
    # add the console handler to the root logger
    logging.getLogger('').addHandler(console_handler)
    # create database tables given defined models (comment out in production)
    with app.app_context():
        db.create_all()
        insert_puns()
    # run the app
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000) # in production, or just app.run()
    # close the console handler to avoid resource leaks
    console_handler.close()
    logging.getLogger('').removeHandler(console_handler)