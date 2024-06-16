import os
import csv
import logging
from flask_login import UserMixin, current_user

# custom
from __init__ import db

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
    rating = db.Column(db.Integer, nullable=False)
    # avg pun rating for a given user
    avg_user_rating = db.Column(db.Float)
    # avg pun rating for the pun across all users
    avg_pun_rating = db.Column(db.Float)

    def __init__(self, user_id, pun_id, rating, avg_user_rating, avg_pun_rating):
        self.user_id = user_id
        self.pun_id = pun_id
        self.rating = rating
        self.avg_user_rating = avg_user_rating
        self.avg_pun_rating = avg_pun_rating

    def store_ratings(
            user_id: int
            , pun_id: int
            , rating: int
            , avg_user_rating: float
            , avg_pun_rating: float
        ):
        new_rating = Ratings(
            user_id=user_id
            , pun_id=pun_id
            , rating=rating
            , avg_user_rating=avg_user_rating
            , avg_pun_rating=avg_pun_rating
        )
        current_user.ratings.append(new_rating)
        db.session.add(new_rating)
        db.session.commit()
