# To obtain a secret key, run the following command in the terminal
# python -c 'import secrets; print(secrets.token_hex())'

import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = '3ddd053b9d4e809538cb02aef5fd9f366f399e6ba27b4396d601c6c023390175'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')