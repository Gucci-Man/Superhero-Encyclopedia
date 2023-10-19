import os

from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError

#from forms import UserAddForm, LoginForm, MessageForm, UserEditForm
from models import db, connect_db, User, Message, Likes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///superheros'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "SUPER TOP SECRET")

connect_db(app)