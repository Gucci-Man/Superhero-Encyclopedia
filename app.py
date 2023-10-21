import os

from flask import Flask, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Favorites
from flask_bcrypt import Bcrypt

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

############################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Route to sign up new user"""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(username=form.username.data, 
                               password=form.password.data,
                               email=form.email.data,
                               image_url=form.image_url.data or User.image_url.default.arg,
                               )
            db.session.commit()

        except IntegrityError as e:
            flash("usernmae already taken", 'danger')
            return render_template('signup.html', form=form)
        
        do_login(user)

        return redirect("/info") #TODO add page and route to list all superheros
        
        
    return render_template("signup.html", form=form)


############################################################################
# General user routes:

@app.route('/info')
def info():
    """Shows grid of superheros to select from"""

    return render_template("info.html")






############################################################################
# Homepage w/ login

@app.route('/', methods=['GET', 'POST'])
def homepage():
    """Show homepage with login and sign-up options"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect('/info') # TODO - add page and route to list all superheros
        
        flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)

##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req