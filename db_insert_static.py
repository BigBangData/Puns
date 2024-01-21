
import os
import csv

from db_model import app, db, Puns, Models

def insert_into_puns():
    try:
        existing_records = Puns.query.first()
        if existing_records is None:
            csv_path = os.path.join('static', 'files', 'puns.csv')
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    new_pun = Puns(question=row['question'], answer=row['answer'])
                    db.session.add(new_pun)
            db.session.commit()
        else:
            print("Data already exists in the Puns table. Skipping insert.")
    except FileNotFoundError:
        print(f"CSV file '{csv_path}' not found.")

def insert_into_models():
    try:
        existing_records = Models.query.first()
        if existing_records is None:
            csv_path = os.path.join('static', 'files', 'models.csv')
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    new_model = Models(
                        short_name=row['short_name']
                        , long_name=row['long_name']
                        , num_votes=row['num_votes']
                        )
                    db.session.add(new_model)
            db.session.commit()
        else:
            print("Data already exists in the Models table. Skipping insert.")
    except FileNotFoundError:
        print(f"CSV file '{csv_path}' not found.")