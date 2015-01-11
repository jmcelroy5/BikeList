from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_oauth import OAuth
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_APP_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///bikelist.db')

db = SQLAlchemy(app)

# Initializing OAuth
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', 'Not set')
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', 'Not set')

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': ('email, ')})

oauth2 = OAuth()

bikeindex = oauth2.remote_app('bikeindex',
    base_url='https://bikeindex.org',
    request_token_url=None,
    access_token_url='/oauth/authorize',
    authorize_url='/oauth/authorize',
    consumer_key='b000781446a184b14193ae041dae1b08b89da22e36523e44d68ab8e878a54d58',
    consumer_secret='486ca32cfa6accc24493031b44ef95b1064214def4550581411e400aa3b7c1d5',
    request_token_params={'scope': ('public'), 'response_type': 'code'})

from app import views, model





