import os
import sys
import site
import logging

logging.basicConfig(stream=sys.stderr)

# Define the path to the virtual environment
venv_path = '/usr/local/venv/py3'

# Add the site-packages of the virtualenv to sys.path
site.addsitedir(os.path.join(venv_path, 'lib/python3.10/site-packages'))

# Set the virtual env
os.environ['VIRTUAL_ENV'] = venv_path
os.environ['PATH'] = os.path.join(venv_path, 'bin') + os.pathsep + os.environ['PATH']

# Add the app/s directory to the PYTHONPATH
sys.path.insert(0, "/var/www/webApp/")

from app import app as application
application.secret_key = 'eujf9e*QW@#_Fe205'