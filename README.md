# Puns

Credits:
- sourced puns from https://wstyler.ucsd.edu/puns/, among other random from memory.

Notes:
- database is for users so far, and any users can create accounts at any time, only usernames and passwords
- this would of course open it to crash the server if someone hit it with creating multiple users, restrict to a few
- use SQL to manage users, in `instance/`, issue:
```
$ sqlite3 database.db
sqlite> .tables
sqlite> select * from user;
sqlite> .exit
```

Functionality:
- signup: only possible when logged out, throws message and redirects to view, fails if username exists
- login: only possible when logged out, throws message and redirects to view
- login: fails back to login when password is wrong, fails to signup when username doesn't exist
- view is the ultimate goal of signing up and logging in, it's where the action happens, and only place logging out is possible
- after logging in, signup/login redirect to view

Ideas:
- 1. Go through questions in order for every user instead of randomly, persist questions asked through sessions [DONE]
    + After user goes through all the questions, start at the beginning again
- 2. Spacy doesn't seem to get answers correct (see below). Try another method such as phonetic similarity [STARTED]
    + So far the word2vec approach is rough, lots of errors to debug.

__NOTE__
- Don't forget to populate the puns table
- Reassess need for separate script, idea is that the table is static and should be part of an app that is constantly running
- Maybe ask chatGPT for help on best practices

__Word Embeddings__

One popular method is to use word embeddings such as Word2Vec, GloVe, or fastText. These embeddings capture semantic relationships between words and might be more suitable for understanding the nuanced similarities in puns. Here's a brief overview of Word2Vec:

1. Word Embeddings Preparation:
    - Download pre-trained Word2Vec embeddings or train your own on a corpus that includes puns.
    - Convert each word in your user's answer and actual answer to its corresponding vector representation.

2. Vector Comparison:
    - Calculate the similarity score between the user's answer and the actual answer by comparing the vectors of individual words.
    - Aggregate these scores to get an overall similarity measure.

3. Threshold Adjustment:
    - Set a threshold based on your observations. Adjust it to find a balance that works for your specific case.

See https://github.com/piskvorky/gensim-data for a list of pre-trained models.


__Phonetic Similarity__

To incorporate phonetic similarity, you can leverage a library that focuses on sound-alike comparisons, such as the Double Metaphone algorithm. This algorithm phonetically encodes words, allowing you to compare their sounds rather than their literal spellings.

Here's an example of how you could integrate Double Metaphone into your comparison function:
```python
    from metaphone import doublemetaphone

    def phonetic_similarity(word1, word2):
        # Get Double Metaphone codes for each word
        code1 = doublemetaphone(word1)
        code2 = doublemetaphone(word2)

        # Check if any of the codes match
        return any(c1 == c2 for c1 in code1 for c2 in code2)

    def compare_texts_phonetic_semantic(text1, text2, phonetic_threshold, semantic_threshold):
        # Tokenize and compare phonetic similarity for each pair of words
        tokens1 = text1.split()
        tokens2 = text2.split()

        # Calculate phonetic similarity scores
        phonetic_scores = [phonetic_similarity(w1, w2) for w1, w2 in zip(tokens1, tokens2)]

        # Calculate semantic similarity as before
        word2vec_similarity = compare_texts_with_word2vec(text1, text2, semantic_threshold)

        # Combine both scores (you can adjust weights based on importance)
        combined_similarity = 0.5 * sum(phonetic_scores) + 0.5 * word2vec_similarity

        # Return 1 if combined similarity is above the thresholds, else return 0
        return 1 if all(score >= phonetic_threshold for score in phonetic_scores) and combined_similarity >= semantic_threshold else 0
```

- Confetti when user gets it right?
- Maybe just embelish view pages, add some images without giving away the answer, or maybe just after giving the answer.
- Maybe add "confetti" every time except instead it's an image related to the answer.
- Unsure how much fun it is to submit and get it wrong too often, maybe instead of congratulating or not,
    just show the scors given the models, and let user see how the model does instead of how user does.


Final Steps:
- figure out security for app.config's secret_key
- use a better algo than bcrypt to hash passwords for chrissakes
- setup so that only a few chosen usernames can signup, password up to them
- deploy to ubuntu server
- follow Tim's last tutorial: https://www.youtube.com/watch?v=YFBRVJPhDGY&list=PLzMcBGfZo4-n4vJJybUVV3Un_NFS5EOgX&index=11

---

## Tutorials

Tutorials from Tim Ruscica: 
- [Flask Series on YouTube](https://www.youtube.com/@TechWithTim)
- [Website](https://www.techwithtim.net)
- [Github](https://github.com/techwithtim)

Tutorial from Arpan Neupane:
- [Authentication Video on YouTube](https://www.youtube.com/watch?v=71EU8gnZqZQ)
- [GitHub](https://github.com/arpanneupane19/Python-Flask-Authentication-Tutorial/blob/main/app.py)

More Links:
- [Bootstrap Intro](https://getbootstrap.com/docs/5.3/getting-started/introduction/)

Blueprint tutorial notes:
- a way to structure entire project and package it so it's usable in other projects
- so for example could create admin folder and in it add templates, static, etc.,
- then could import from admin by packaging folder (create __init__.py empty file inside folder)