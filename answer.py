import spacy

# custom
from flask_login import current_user
from db_model import db, Answer

# Spacy text similarity
# ---------------------
# Load English model to compare answers
# downloaded with: python -m spacy download en_core_web_md
nlp = spacy.load("en_core_web_md")

def compare_answer_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    # compute similary score
    score = doc1.similarity(doc2)
    # compare with threshold
    # return 1 if score >= threshold else 0
    return score

# Answer table
# ------------
# Store answer, including scores, in database
def store_answer(user_id, pun_id, user_answer, score):
    new_answer = Answer(
        user_id=user_id
        , pun_id=pun_id
        , user_answer=user_answer
        , score=score
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()