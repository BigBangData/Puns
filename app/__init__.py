import os
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# setup flask app
app = Flask(__name__)
#csrf = CSRFProtect()
#csrf.init_app(app)

# store session data for 5 min; works even if browser is open
app.permanent_session_lifetime = timedelta(minutes=5)

# setup database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# uncomment for creating new database from scratch
if 'sqlalchemy' in app.extensions:
    del app.extensions['sqlalchemy']

# instantiate database
db = SQLAlchemy(app)