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
- Spacy doesn't seem to get answers correct (see below). Try another method such as phonetic similarity.
- Jenny wants confetti when user gets it right.
- Embelish view pages, add some images without giving away the answer, or maybe just after giving the answer.
- Maybe add "confetti" every time except instead it's an image related to the answer.
- Unsure how much fun it is to submit and get it wrong too often, maybe instead of congratulating or not,
    just show the scors given the models, and let user see how the model does instead of how user does.

Tech Debt:
```
app.py:45: LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy 
and becomes a legacy construct in 2.0. The method is now available as Session.get() (deprecated since: 2.0) 
(Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    return User.query.get(int(user_id))
```

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