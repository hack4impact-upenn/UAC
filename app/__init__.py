from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os
from flask.ext.mail import Mail

basedir = os.path.abspath(os.path.dirname(__file__))

# Use a Class-based config to config flask and extensions
class ConfigClass(object):
    # Flask settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     
        'sqlite:///' + os.path.join(basedir, 'test.db'))    
    DEBUG = True

    #email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'yoninachmany@gmail.com'
    MAIL_PASSWORD = 'rsifgordritrxfxf'

    # administrator list
    ADMINS = ['yoninachmany@gmail.com']

app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)
mail = Mail(app)

from app import views