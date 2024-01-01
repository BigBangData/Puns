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
- signup is always possible, even for logged in users (can signup as another user, but not login)
- signup username must be unique
- login only possible if not currently logged in, throws message and redirects to view
- logout only possible in view
- view is the ultimate goal, where the "game" happens

Todo:
- change view to the pun game
- `curated_puns.txt`: manually curated text file that serves as input to create the database; in question?answer format
- just read directly from `curated_puns.txt` no need to create a database for puns

Final Steps:
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