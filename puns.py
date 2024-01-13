
import os
import csv

from db_model import app, db, Puns

# load data from CSV and populate the puns table
def populate_puns():
    try:
        csv_path = os.path.join('static', 'files', 'puns.csv')
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                new_pun = Puns(question=row['question'], answer=row['answer'])
                db.session.add(new_pun)
        db.session.commit()
    except FileNotFoundError:
        print(f"CSV file '{csv_path}' not found.")

if __name__=="__main__":
    with app.app_context():
        populate_puns()