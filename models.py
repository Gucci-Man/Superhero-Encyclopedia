"""SQLAlchemy models for Superhero/Villain Encyclopedia"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system"""

    __tablename__='users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    # TODO - add default image
    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    favorites = db.relationship('Favorites')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}"
    
    @classmethod
    def signup(cls, username, password, email, image_url):
        """Sign up user,

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.

        If can't find matching user (or if password is wrong), return False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            
        return False


class Favorites(db.Model):
    """Mapping a user favorite characters"""

    __tablename__ = 'favorites'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    """ superhero_id = db.Column(
        db.Integer,
        db.ForeignKey('superheros.id', ondelete='cascade')
    ) """

    # id from API, so no need to set as foreign key
    superhero_id = db.Column(
        db.Integer,
    )

    rating = db.Column(
        db.Integer,
    )



# TODO - would I want to create SQL tables for superheros if I am pulling data from APU?
""" class Superhero(db.Model):

    # superhero information
    
    # If saving in database, we could add information like ratings and/or reviews
    

    __tablename__ = 'superheros'

    id = db.Column(
        db.Integer,
        primary_key=True,
    ) """

def connect_db(app):
    """Connecting this database to the lask app."""

    db.app = app
    db.init_app(app)


