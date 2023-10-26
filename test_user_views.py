"""User View tests"""

# run these tests like:
#
#    python3 -m unittest test_views_model.py

from unittest import TestCase
from app import app, CURR_USER_KEY
from models import db, User, Favorites
from flask import session

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///superheros_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

db.create_all()

class UserViewsTestCase(TestCase):
    """Tests for views of the Superhero Encyclopedia"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        # Create test user
        u1 = User.signup("test1", "password1", "email1@email.com", None)
        uid1 = 111
        u1.id = uid1

        db.session.commit()

        u1 = User.query.get(uid1)

        self.u1 = u1
        self.uid1 = uid1

        # Create test favorite w/ Groot
        hid1 = 303 
        self.hid1 = hid1

        # Test user will have one favorite
        fav1 = Favorites(user_id=uid1, hero_id=hid1)

        db.session.add(fav1)
        db.session.commit()

        self.fav1 = fav1

        # hero_id of Nick Fury for testing
        hid2 = 489
        self.hid2 = hid2

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()