# Puns

Credits:
- sourced puns from https://wstyler.ucsd.edu/puns/, among others.
- `curated_puns.txt`: manually curated text file that serves as input to create the database; in question?answer format

Tutorials:
- followed: https://www.youtube.com/watch?v=71EU8gnZqZQ
    - GitHub: https://github.com/arpanneupane19/Python-Flask-Authentication-Tutorial/blob/main/app.py
- did not follow Tim's: https://www.youtube.com/watch?v=W4GItcW7W-U 
    - GitHub: https://github.com/techwithtim/Flask-Blog-Tutorial
- just read directly from `curated_puns.txt` no need to create a database for puns

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

Next Steps:
- test going from login to view to home etc and think through various flows again to flash messages
    + it's a bit of a hybrid of tutorials, so look at commented out code for user flows
- right now functionality is very limited and logout only exists in `view.html`
- recreate `view.html` to be a dashboard for puns and not a user management page

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