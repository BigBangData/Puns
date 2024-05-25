from flask_wtf import FlaskForm
from flask_login import LoginManager
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
# custom
from db_model import app, User

# security & login
ph = PasswordHasher()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# reload user object from user_id stored in session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Username is required."),
            Length(min=6, max=20, message="Username must be between 6 and 20 characters.")
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
        if len(username.data) < 6 or len(username.data) > 20:
            return  # Skip checking existing user if length is invalid

        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError("User exists.")

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Username is required."),
            Length(min=6, max=20, message="Username must be between 6 and 20 characters.")
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

# Utility functions for hashing and checking passwords
def hash_password(password):
    return ph.hash(password)

def check_password_hash(hashed_password, plain_password):
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False