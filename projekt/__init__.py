#imports
import os
import pymongo
import sendgrid
from pymongo import Connection
#from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask.ext.wtf import Form, TextField, TextAreaField, \
    PasswordField, SubmitField, Required, ValidationError
from flask.ext.bcrypt import Bcrypt, generate_password_hash, \
	check_password_hash
import flask_sijax	

#define app
app = Flask(__name__)

app.config['SIJAX_STATIC_PATH'] = os.path.join('.',os.path.dirname(__file__), 'static/js/sijax')

app.config['UPLOADED_FILES_DEST'] = os.path.join('.', os.path.dirname(__file__),'static/img/uploadedmedia')

SENDGRID_USERNAME= ""
SENDGRID_PASSWORD= ""

mailer = sendgrid.Sendgrid(SENDGRID_USERNAME, SENDGRID_PASSWORD, secure=True)

#initialize flask_sijax
flask_sijax.Sijax(app)

#define bcrypt
bcrypt = Bcrypt(app)

#define the configuration
app.config.from_pyfile('config.cfg')

#conn = Connection('localhost', 45000)
MONGO_URI = ""
MONGO_DB = ""
conn = Connection(MONGO_URI)
db = conn[MONGO_DB]

events = db['events']
users = db['users']

#imports forms models and views
import projekt.forms
import projekt.views