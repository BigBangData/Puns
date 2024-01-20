# Puns

__Credits__
- sourced puns from https://wstyler.ucsd.edu/puns/, among other random from memory
- tutorials (link to end)

__Notes__
- any user can create an account at any time, only usernames and passwords
- this would of course open it to crash the server if someone hit it with creating multiple users, restrict to a few
- use SQL to manage users, in `instance/`, issue:
```
$ sqlite3 database.db
sqlite> .tables
sqlite> select * from user;
sqlite> .exit
```
- after launching app, populate the puns table via `python populate_puns.py` (only once)

__Functionality__
- signup: only possible when logged out, throws message and redirects to view, fails if username exists
- login: only possible when logged out, throws message and redirects to view
- login: fails back to login when password is wrong, fails to signup when username doesn't exist
- view: goal of signing up and logging in, where the action happens, and only place logging out is possible
  + after logging in, signup/login redirect to view
- view:
  + goes through questions in order for every user
  + persist questions asked beyond single session
  + starts over when all questions have been asked for a given user
  + does matching in two ways: spacy text (looks to be semantic?) and phonetic

__Backlog__
- Try some other models here: https://chat.openai.com/share/17fac774-7de9-4e9b-b41b-2bcc7eba708f
  + evaluating results in qa/
- Change "view.html" to "puns.html" or "play.html"
- Average scores and set a threshold for success
- Add success messages and confetti or images
- Add hints or at least how many words the answer contains
- Add a "go back to last one" button
- Add a grid with numbers for all the puns or a select by number
- Strip user input of newlines _before_ matching
- Strip user inpute for security reasons
- Use a better algo than bcrypt to hash passwords
- Delete all the logging.info of <SecureCookieSession> and others

__Discarded__
- Word embeddings in `word2vec` were cumbersome, slowed down the app, and yielded dubious results
- Spacy's `en_core_web_trf` yielded 0.0 similarity scores; mostly for longer texts

__Final Steps__
- Figure out security for app.config's secret_key
- Maybe setup so that only a few chosen usernames can signup, password up to them
- Deploy (follow Tim's last tutorial)

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

---

## Discarded Methods

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

---