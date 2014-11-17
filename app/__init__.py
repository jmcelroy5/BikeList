from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'A0Zr98j/32345(679R~XHH!jmN]LWX/,?RT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bikelist.db'

db = SQLAlchemy(app)

from app import views, model