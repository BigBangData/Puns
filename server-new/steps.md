## Server Deployment Steps

1. install pip: `sudo apt install python3-pip`
2. install virtualenv: `sudo apt install python3-virtualenv`
3. create a virtualenv in /usr/local/venv dir: `/usr/local/venv# virtualenv -p /usr/bin/python3 py3`
4. activate it in correct folder: `/var/www/webApp# source /usr/local/venv/py3/bin/activate`
5. install packages from requirements: `(py3) /var/www/webApp# pip install -r requirements.txt`
6. install wsgi: `sudo apt-get install libapache2-mod-wsgi-py3 python-dev-is-python3`

1. clone repo or transfer files for app; remember to `mkdir logs static instance`
2. create `webapp.wsgi` file in `webApp/`
3. modify `__init__.py` for secret key and database url and `main.py` to use `app.run()`
4. create wsgi conf file: `vi /etc/apache2/sites-available/webApp.conf`
5. (option) remove old conf file: `rm /etc/apache2/sites-enabled/webApp.conf`
6. renable conf: `a2ensite webApp.conf`
7. (re)start server: `systemctl start apache2`

## Troubleshooting
- Homepage is found but Signup doesn't work because there are no tables in the database
    + attempt to create database locally and move it to the server with a couple approved users
    + restructure code since beta users portion won't work

