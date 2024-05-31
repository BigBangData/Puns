# Copyright 2024 Marcelo Sanches
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import csv
import logging

# custom
from .db_model import db, Puns, Models

def insert_into_puns():
    try:
        existing_records = Puns.query.first()
        if existing_records is None:
            csv_path = os.path.join('app', 'static', 'files', 'puns_hints.csv')
            with open(csv_path, mode='r', encoding='utf-8-sig') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                row_count = 0
                for row in csv_reader:
                    new_pun = Puns(
                        question=row['question']
                        , answer=row['answer']
                        , hint=row['hint']
                    )
                    db.session.add(new_pun)
                    row_count += 1
                logging.info(f"Inserted {row_count} rows into Puns.")
            db.session.commit()
        else:
            logging.info("Skipped Insert - table Puns already exists.")
    except FileNotFoundError:
        logging.error(f"CSV file '{csv_path}' not found.")

def insert_into_models():
    try:
        existing_records = Models.query.first()
        if existing_records is None:
            csv_path = os.path.join('app', 'static', 'files', 'models.csv')
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                row_count = 0
                for row in csv_reader:
                    new_model = Models(
                        short_name=row['short_name']
                        , long_name=row['long_name']
                        , num_votes=row['num_votes']
                    )
                    db.session.add(new_model)
                    row_count += 1
                logging.info(f"Inserted {row_count} rows into Models.")
            db.session.commit()
        else:
            logging.info("Skipped Insert - table Models already exists.")
    except FileNotFoundError:
        logging.error(f"CSV file '{csv_path}' not found.")
