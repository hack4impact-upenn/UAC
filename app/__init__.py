from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Use a Class-based config to config flask and extensions
class ConfigClass(object):
    # Flask settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     
        'sqlite:///' + os.path.join(basedir, 'test.db'))    
    DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)

from app import views