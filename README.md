# Puns

Sourced puns from https://wstyler.ucsd.edu/puns/, among others.

- curated_puns.txt:
    must have a Q?A format

Tutorials: https://www.youtube.com/watch?v=9MHYHgh4jYc&list=PLzMcBGfZo4-n4vJJybUVV3Un_NFS5EOgX&index=6
Bootstrap: https://getbootstrap.com/docs/5.3/getting-started/introduction/

Solved:
    - a logged out user can log out, doesn't display 'successful logout' if no one is logged in
    - a user can only view and delete their own entry in the database
    - added logs and logging info to debug issues and see in realtime what is gonig on

Issues:
    - assumes name doesn't repeat in database, so no two different entires for the same name can exist
    - need to create an admin login either as separate page or as separate user in the view func
    - admin should be able to view all users (right now we can't)
    - create separate form to delete email
    - maybe logout user if user is deleted
    - ideally ask to create account instead of just creating one
