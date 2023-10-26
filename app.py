import os

from flask import Flask, render_template, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Favorites
from api_requests import get_request

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

        return redirect("/superheros") #TODO add page and route to list all superheros
        
        
    return render_template("signup.html", form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", "success")
    return redirect('/')

############################################################################
# User routes:

@app.route("/users/<int:user_id>")
def show_details(user_id):
    """Show user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)


@app.route("/users/edit", methods=['GET', 'POST'])
def edit_user():
    """Route to edit user profile"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data
        user.location = form.location.data
        user.bio = form.bio.data

        db.session.commit()
        return redirect(f"/users/{user.id}")
    
    return render_template('edit.html', form=form, user=user)


@app.route("/users/delete", methods=["GET", "POST"])
def delete_user():
    """Delete User"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    do_logout()
    
    # Deleting user favorites
    Favorites.query.filter_by(user_id=g.user.id).delete()

    db.session.delete(g.user)
    db.session.commit()

    flash("User Deleted", "info")
    return redirect("/")

# TODO - let user go to the superhero info page when clicking on favorite superhero
# TODO - Show favorite superheros as a table
@app.route("/users/favorites")
def user_favs():
    """Page for user favorites"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    # To store the user favorite heros and send to page
    fav_heros = []
    
    # Retrieve list of hero ids from user favorites to get superhero info
    fav_list = g.user.favorites
    id_list = [fav.hero_id for fav in fav_list]

    # Create superhero object from API request and add to list for page
    for hero_id in id_list:
        superhero = get_request(hero_id)
        fav_heros.append(superhero)

    return render_template("favorites.html", fav_heros=fav_heros, user=g.user)
############################################################################
# Main encyclopedia routes:

@app.route('/superheros')
def info():
    """Shows grid of superheros to select from"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    user = User.query.get_or_404(g.user.id)
    print(f"user is {user}")

    return render_template("info.html", user=user)


@app.route("/superheros/<int:hero_id>")
def hero_info(hero_id):
    """Show detailed info of superhero"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    # Make API request then store response in data
    superhero = get_request(hero_id)

    # Retrieve list of hero ids from user favorites
    # To check if this superhero is a user favorite
    fav_list = g.user.favorites
    id_list = [str(fav.hero_id) for fav in fav_list]

    return render_template("hero.html", superhero=superhero, id_list=id_list)


@app.route("/superheros/<int:hero_id>/fav", methods=['POST'])
def fav_hero(hero_id):
    """Adding/removing superhero from user favorites"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')
    
    # Retrieve the superhero that was favorited if it already is
    fav_hero = Favorites.query.filter_by(hero_id=hero_id, user_id=g.user.id).first()

    # If that superhero is already favorited, then un-favorite it
    # If favorite doesn't exist, then add to favorites
    fav_list = g.user.favorites

    if fav_hero in fav_list:
        print("Favorite has to be unliked")
        Favorites.query.filter_by(hero_id=hero_id, user_id=g.user.id).delete()
    else:
        add_fav = Favorites(hero_id=hero_id, user_id=g.user.id)
        db.session.add(add_fav)
    
    db.session.commit()
    return redirect(f"/superheros/{hero_id}")



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
            return redirect('/superheros') # TODO - add page and route to list all superheros
        
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