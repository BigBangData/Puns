# Puns

_Credits &tc ~_
- sourced puns from https://wstyler.ucsd.edu/puns/, among others.
- `curated_puns.txt`: manually curated text file that serves as input to create the database; in question?answer format

_Brainstorm ~_
- instead of creating account, password, email... just have a login page and my friends must be "in the know"
    + watch tutorials for logging in?
    + candidate 1: https://www.youtube.com/watch?v=71EU8gnZqZQ
        - following: https://github.com/arpanneupane19/Python-Flask-Authentication-Tutorial/blob/main/app.py
        - at min 18:30
    + candidate 2: https://www.youtube.com/watch?v=W4GItcW7W-U # Tim
        - GitHub: https://github.com/techwithtim/Flask-Blog-Tutorial
- just read directly from `curated_puns.txt` no need to create a database for v1




---

## Old Notes

Tutorials from Tim Ruscica: https://www.youtube.com/@TechWithTim, https://www.techwithtim.net/, https://github.com/techwithtim

Bootstrap: https://getbootstrap.com/docs/5.3/getting-started/introduction/

Blueprint tutorial notes:
- a way to structure entire project and package it so it's usable in other projects
- so for example could create admin folder and in it add templates, static, etc.,
- then could import from admin by packaging folder (create __init__.py empty file inside folder)
- not going to use this knowledge for this project, focus on deliverable

Solved:
- a logged out user can log out, doesn't display 'successful logout' if no one is logged in
- a user can only view and delete their own entry in the database
- added logs and logging info to debug issues and see in realtime what is going on

Issues:
- assumes name doesn't repeat in database, so no two different entires for the same name can exist
- need to create an admin login either as separate page or as separate user in the view func
- admin should be able to view all users (right now we can't)
- create separate form to delete email
- maybe logout user if user is deleted
- ideally ask to create account instead of just creating one