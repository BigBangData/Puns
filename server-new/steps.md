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
    + attempt to create database locally and scp it to the server
    + restructure code to avoid signup altogether (beta users exposed in code)
    + database users: spicamia, huzzah, pass: courageous

- scp file transfer with private key to move files (database)
- change permissions because I got an error that the database was read-only
- changed permissions only to the apache database user, www-data:
    `sudo chown www-data:www-data /var/www/webApp/instance/database.db`
    `sudo chmod 664 /var/www/webApp/instance/database.db`
- to both file and folder:
    `sudo chown www-data:www-data /var/www/webApp/instance`
    `sudo chmod 775 /var/www/webApp/instance`
- this presumes in `webApp.conf` the user is `www-data`:
    `WSGIDaemonProcess flaskapp user=www-data group=www-data threads=5`

- got this error because of the javascript to throw confetti: 
    `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xed in position 296: invalid continuation byte`
- solved by removing the javascript from the `view_answer.html` page
- knew it was the script upon inspecing using UTF-8 (button lower right) to reload the file and inspect errors
- could also use Notepad++:
    + Open the file in Notepad++. Go to Encoding in the menu.
    + Ensure Encode in UTF-8 is selected. If not, select Convert to UTF-8.
- could open in binary:
```
with open('/path/to/your/view_answer.html', 'rb') as file:
    content = file.read()
    print(content)
```

