import os
import spacy

from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity

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

# Word2Vec word embeddings
# ------------------------
# Load previously downloaded Word3Vec model
# downloaded with auxiliary script
# model_name = 'word2vec-google-news-300'
# model_path = os.path.join('~', 'Documents', 'GitHub', 'Puns', 'models', model_name)
# Specify the full path to the model directory
model_directory = os.path.expanduser('~/Documents/GitHub/Puns/models')

# Specify the model name without the extension
model_name = 'word2vec-google-news-300'

# Load the Word2Vec model
model_path = os.path.join(model_directory, model_name)
w2v_model = KeyedVectors.load(model_path)

def get_mean_cosine_similarity(text1, text2):
    # Tokenize and get vectors for each word in the texts
    tokens1 = [word for word in text1.split() if word in w2v_model.key_to_index]
    tokens2 = [word for word in text2.split() if word in w2v_model.key_to_index]
    # Calculate cosine similarity between the vectors
    try:
        similarity_scores = cosine_similarity(w2v_model[tokens1], w2v_model[tokens2])
        # Calculate the average similarity score
        avg_similarity = similarity_scores.mean()
        # return 1 if avg_similarity >= thresh else 0
    except ValueError:
        avg_similarity = 0
    return avg_similarity

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