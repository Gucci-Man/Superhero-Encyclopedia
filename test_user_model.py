""""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


from unittest import TestCase
from models import db, User, Favorites
from flask import session
from app import app


# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///superheros_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, not HTML pages with error info
app.config["TESTING"] = True

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False


db.create_all()


class UserModelTestCase(TestCase):
    """Testing User Model"""

    def setUp(self):
        """Create test user, add sample data."""

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

        fav1 = Favorites(user_id=uid1, hero_id=hid1)

        db.session.commit()

        self.fav1 = fav1

        # hero_id of Nick Fury for testing
        hid2 = 489
        self.hid2 = hid2




    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()
        

    
    def test_user_model(self):
        """Testing basic user model"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="PasswordTest"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no favorites yet
        self.assertEqual(len(u.favorites), 0)


    ####
    #
    # User Favorite's test
    # 
    ####

    def test_add_favorite(self):
        """Test adding a favorite"""

        # Test adding Nick Fury as favorite
        fav_test = Favorites(user_id=self.uid1, hero_id=self.hid2)

        db.session.add(fav_test)
        db.session.commit()

        # Test that favorite is linked to user
        fav_test = Favorites.query.filter_by(user_id=self.uid1).first()
        self.assertEqual(fav_test.user.username, "test1")

        