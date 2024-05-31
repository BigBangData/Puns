# Puns

![License](https://img.shields.io/github/license/BigBangData/Puns)
![File Count](https://img.shields.io/github/directory-file-count/BigBangData/Puns)
![Last Commit](https://img.shields.io/github/last-commit/BigBangData/Puns?color=blueviolet)
![Stars](https://img.shields.io/github/stars/BigBangData/Puns?style=social)
![Forks](https://img.shields.io/github/forks/BigBangData/Puns?style=social)
![Watchers](https://img.shields.io/github/watchers/BigBangData/Puns?style=social)

## Story

I created this little puns game on a whim but also because I wanted to learn how to deploy a site using Python and Flask. At first the game was just showing puns plus a "next pun" button, then it evolved into a question-and-answer format to get more user interaction and apply some data science tooling to compute similarity scores for user answers and actual answers. Finally I realized I could get user feeback to help train an online system, which is the current version.

The site is hosted [INSERT_LINK](INSERT_LINK).

## Demo

Add a demo gif

## Features

Below are some features or behaviors of the frontend:

- __signup__: 
  + only possible when logged out, throws message and redirects to `play`, fails if username exists
- __login__: 
  + only possible when logged out, throws message and redirects to `play`
  + fails to `login` when password is wrong, fails to `signup` when username doesn't exist
  + session `logout` user after inactivity
- __play__: 
  + goal of `signup` and `login`
  + only place `logout` is possible
  + after `login`, either `signup` or `login` will redirect to `play`
  + goes through questions in order for every user
  + persist questions asked beyond single session so user can come back where she left off
  + starts over when all questions have been asked for a given user
- __view answer__:
  + view actual answer and own answer
  + see a message that reflects whether own answer was correct or not
  + if own answer is correct, unicorn confetti are thrown; if not, lobster confetti are thrown
  + user can click on an `AGREE` or a `DISAGREE` button to provide feedback
    - this action is the only way to load the next question (redirecting to `play`)
      + in the backend, this user feedback increments the weights for the model which performed the best
      + over time, that should improve the accuracy of the system, which uses weighted averages and a threshold to determine success
      + user input is stored in a table with all the answers, including success or failure, etc.
    - fun fact: clicking on `play` again without providing feedback reloads the same question
  + view model "leaderboard" with match scores (similarity scores for the current user and actual answers)
    - challenge: since the weighted avg score is provided, can the user compute the weights from the information given?

## Backlog

- Address CSFR
- Setup for a few beta testers
- Deploy

## Idealog

- Add a "view your answers" button that redirects to a page with user stats
- Add a "suggest a hint" button for disgruntled users
- Handle explanation of "he was a little horse" vs "he was a little hoarse" (which is the "correct pun"?)

## Credits

- Originally sourced many of the puns (the `raw_puns.txt`) from https://wstyler.ucsd.edu/puns/
  + I'd populate the puns table via `python populate_puns.py` (flow was `raw_puns.txt >> curated_puns.txt >> puns.csv`)
- Started adding my own as time went by, also reformatted original puns to fit the Q&A format and added hints
  + a `Puns` table is created using `puns_hints.csv` (saved as CSV-BOM-8 from `puns_hints.xlsx`)
- The point of origin for some of the app's code was Tim Ruscica's tutorials below, and Arpan Neupane's turotial for authentication
- I also made use of chatGPT (free tier of https://chat.openai.com/) to help with some coding challenges 

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

__Note__

I did not follow the blueprint tutorial but might one day. It's a way to structure an entire project and package it so it's usable in other projects. For example, one could create an `admin` folder and add add templates, static, etc. to it and simply `import admin` by packaging the folder with an empty `__init__.py` file.

## Discarded Methods

- I thought that the semantic relationships in word embeddings like `Word2Vec`, `GloVe`, or `fastText` might be more suitable for understanding the nuanced similarities in puns. Turns out word embeddings in `Word2Vec` were cumbersome, slowed down the app, and yielded dubious results. 


- Spacy's `en_core_web_trf` yielded 0.0 similarity scores. It seems to be mostly useful for longer texts.


---