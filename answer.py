import spacy
import numpy as np
from typing import List
from fuzzywuzzy import fuzz
from metaphone import doublemetaphone
from sentence_transformers import SentenceTransformer, util

# custom
from flask_login import current_user
from db_model import db, Answer

# Spacy
# -----
web_sm = spacy.load("en_core_web_sm")
web_md = spacy.load("en_core_web_md")

# Sentence Transformers
# ---------------------
all_st = SentenceTransformer("all-MiniLM-L6-v2")
par_st = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_similarity_score(text1, text2, model, transf: bool=False):
    """Get cosine similarity score given two texts and a model.
    """
    if transf:
        embeddings1 = model.encode(text1, convert_to_tensor=True)
        embeddings2 = model.encode(text2, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2).item()
    else:
        document1 = model(text1)
        document2 = model(text2)
        similarity_score = document1.similarity(document2)
    return similarity_score

def get_web_sm_similarity(text1, text2, model=web_sm):
    return get_similarity_score(text1, text2, model)

def get_web_md_similarity(text1, text2, model=web_md):
    return get_similarity_score(text1, text2, model)

def get_all_st_similarity(text1, text2, model=all_st):
    return get_similarity_score(text1, text2, model, transf=True)

def get_par_st_similarity(text1, text2, model=par_st):
    return get_similarity_score(text1, text2, model, transf=True)


# Phonetic Matching
# -----------------
def match_words_by_sound(word1, word2, debug=False):
    """Helper function for calculate_phonetic_fuzzy_similarity()"""
    # get double metaphone codes for each word
    code1 = doublemetaphone(word1)
    code2 = doublemetaphone(word2)
    # calculate primary and secondary matches
    primary_match = (code1[0] == code2[0] or code1[1] == code2[0])
    secondary_match = (code1[0] == code2[1] or code1[1] == code2[1])
    # return when both match
    match = primary_match and secondary_match
    if debug:
        print(f"code1: {code1}")
        print(f"code2: {code2}")
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
def store_answer(user_id: int, pun_id: int, user_answer: str, scores: List[float]):
    new_answer = Answer(
        user_id=user_id,
        pun_id=pun_id,
        user_answer=user_answer,
        scores=scores
    )
    current_user.answers.append(new_answer)
    db.session.add(new_answer)
    db.session.commit()