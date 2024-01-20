import spacy
import numpy as np
from fuzzywuzzy import fuzz
from metaphone import doublemetaphone

# custom
from flask_login import current_user
from db_model import db, Answer

# Spacy text similarity
# ---------------------
# Load English models to compare answers
md_nlp = spacy.load("en_core_web_md")
sm_nlp = spacy.load("en_core_web_sm")

def get_text_similarity_score(text1, text2, model):
    """Get text similarity score given two texts and a model"""
    doc1 = model(text1)
    doc2 = model(text2)
    t_score = doc1.similarity(doc2)
    return t_score

def get_md_text_similarity(text1, text2, model=md_nlp):
    return get_text_similarity_score(text1, text2, model)

def get_sm_text_similarity(text1, text2, model=sm_nlp):
    return get_text_similarity_score(text1, text2, model)

# Phonetic Matching
# -----------------
def match_words_by_sound(word1, word2, debug=False):
    """Helper function for calculate_phonetic_fuzzy_similarity()"""
    # get double metaphone codes for each word
    a = doublemetaphone(word1)
    b = doublemetaphone(word2)
    # calculate primary and secondary matches
    primary_match = (a[0] == b[0] or a[1] == b[0])
    secondary_match = (a[0] == b[1] or a[1] == b[1])
    # return when both match
    match = primary_match and secondary_match
    if debug:
        print(f"a: {a}")
        print(f"b: {b}")
        print(f"primary_match: {primary_match}")
        print(f"secondary_match: {secondary_match}")
        print(f"match: {match}")
    return match

def get_phonetic_fuzzy_similarity(text1, text2, debug=False):
    # tokenize texts into words
    words1 = text1.split()
    words2 = text2.split()
    # encode words using double metaphone
    m1 = [doublemetaphone(word) for word in words1]
    m2 = [doublemetaphone(word) for word in words2]
    # flatten the list of metaphones
    flat_m1 = [pho for m_pair in m1 for pho in m_pair]
    flat_m2 = [pho for m_pair in m2 for pho in m_pair]
    # calculate similarity using Fuzzywuzzy
    similarity_score = fuzz.ratio(" ".join(flat_m1), " ".join(flat_m2))
    # return normalized score
    normalized_score = np.round(similarity_score / 100, 2)
    if debug:
        print(f"Words 1: {words1}")
        print(f"Words 2: {words2}")
        print(f"Metaphones 1: {m1}")
        print(f"Metaphones 2: {m2}")
        print(f"Flattened Metaphones 1: {flat_m1}")
        print(f"Flattened Metaphones 2: {flat_m2}")
    return normalized_score

# Answer table
# ------------
# Store answer, including scores, in database
def store_answer(
        user_id
        , pun_id
        , user_answer
        , md_txt_sim_score
        , sm_txt_sim_score
        , phonetic_fuzzy_sim_score
    ):
    new_answer = Answer(
        user_id=user_id
        , pun_id=pun_id
        , user_answer=user_answer
        , md_txt_sim_score=md_txt_sim_score
        , sm_txt_sim_score=sm_txt_sim_score
        , phonetic_fuzzy_sim_score=phonetic_fuzzy_sim_score
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()