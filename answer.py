import spacy
from metaphone import doublemetaphone

# custom
from flask_login import current_user
from db_model import db, Answer

# Spacy text similarity
# ---------------------
# Load English model to compare answers
# downloaded with: python -m spacy download en_core_web_md
nlp = spacy.load("en_core_web_md")

def compare_text_similarity(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    # compute similary score
    t_score = doc1.similarity(doc2)
    # compare with threshold
    # return 1 if score >= threshold else 0
    return t_score

def phonetic_similarity(word1, word2):
    # Get Double Metaphone codes for each word
    code1 = doublemetaphone(word1)
    code2 = doublemetaphone(word2)
    # Check if any of the codes match
    return any(c1 == c2 for c1 in code1 for c2 in code2)

def compare_phonetic_similarity(text1, text2):
    # Tokenize and compare phonetic similarity for each pair of words
    tokens1 = text1.split()
    tokens2 = text2.split()
    # calculate phonetic similarity scores
    phonetic_scores = [phonetic_similarity(w1, w2) for w1, w2 in zip(tokens1, tokens2)]
    # sum scores
    p_score = sum(phonetic_scores)
    return p_score

# Answer table
# ------------
# Store answer, including scores, in database
def store_answer(user_id, pun_id, user_answer, t_score, p_score):
    new_answer = Answer(
        user_id=user_id
        , pun_id=pun_id
        , user_answer=user_answer
        , text_similarity_score=t_score
        , phonetic_similarity_score=p_score
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()