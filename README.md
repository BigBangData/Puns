# Puns

![License](https://img.shields.io/github/license/BigBangData/Puns)
![File Count](https://img.shields.io/github/directory-file-count/BigBangData/Puns)
![Last Commit](https://img.shields.io/github/last-commit/BigBangData/Puns?color=blueviolet)
![Stars](https://img.shields.io/github/stars/BigBangData/Puns?style=social)
![Forks](https://img.shields.io/github/forks/BigBangData/Puns?style=social)
![Watchers](https://img.shields.io/github/watchers/BigBangData/Puns?style=social)

## Story

I created this little puns game on a whim but also because I wanted to learn how to deploy a site using Python and Flask. At first the game was just showing puns plus a "next pun" button, then it evolved into a question-and-answer format to get more user interaction and apply some data science tooling to compute similarity scores for user answers and actual answers. Finally I realized I could get user feeback to help train an online system, which is the current version.

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
  + goes through puns in order for every user
  + shows only question and word count so user can try to guess
  + any key redirects to `view_answer.html`
  + persist puns asked beyond single session so user can come back where she left off
  + starts over when all puns have been shown
- __view answer__:
  + reveals answer and pun
  + user must click on one of three buttons for feedback: sigh, eyeroll, groan
  + feedback get recorded in the backend table of ratings, and triggers new `play` (POST)
  + page also shows user stats (how many of each feedback)


## Local Dev

```
source ~/usr/local/venv/py3/Scripts/activate
source local.env
python -u run.py
```

__Dev Flow__
- commit changes
- copy changes into `server/` to see diff
- revert changes that aren't needed in the server
- scp changes into server
- ssh, modify user and permissions and restart apache

## Backlog

- Create better stats UX (barplot)
- Add more puns
- Finalize README
- Redeploy (keep SpicaMia's history)

## Reproducibility

- `static/files/raw_puns.txt` has original puns drawn from life or the web (see credits)
- `static/files/curated_puns.txt` has puns curated into Q&A form (original intent of the site)
- `python populate_puns.py` creates `statis/files/puns.csv` which is used by the backend to populate a `Puns` table

## Credits

- many of the puns were originally sourced from Will Styler's collection at: https://wstyler.ucsd.edu/puns/
- the point of origin for some of the app's code was Tim Ruscica's tutorials below, and Arpan Neupane's turotial for authentication
- I also made regular use of chatGPT (free tier of https://chat.openai.com/) to help speed up and troubleshoot code and deployment

## Tutorials Consulted

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