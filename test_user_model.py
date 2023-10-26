""""User model tests."""

# run these tests like:
#
#    python3 -m unittest test_user_model.py


from unittest import TestCase
from sqlalchemy import exc
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
    # Signup Tests
    #
    ####

    def test_valid_signup(self):
        """Test that signing up is valid"""

        test_user = User.signup("testtest", "testpass", "testtest@test.com", None)
        uid = 555
        test_user.id = uid
        db.session.commit()

        test_user = User.query.get(uid)

        # Should be an instance of user
        self.assertIsInstance(test_user, User)
        self.assertEqual(test_user.username, "testtest")
        self.assertEqual(test_user.email, "testtest@test.com" )

        # Password should be encrypted
        self.assertNotEqual(test_user.password, "testpass" )
        self.assertTrue(test_user.password.startswith("$2b"))


    def test_invalid_username_signup(self):
        """Test signing up without a username"""

        test_user = User.signup(None, "testpass", "testtest@test.com", None)
        uid = 1234
        test_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """Test signing up with an email"""

        test_user = User.signup("testtest", "testpass", None, None)
        uid = 4321
        test_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Test signing up with invalid password"""

        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "", "testtest@test.com", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", None, "testtest@test.com", None)

    ####
    #
    # Authentication Tests
    # 
    ####

    def test_valid_authentication(self):
        """Test authentication works"""

        u = User.authenticate(self.u1.username, "password1")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
    
    def test_invalid_username(self):
        """Test authentication fails with invalid username"""

        self.assertFalse(User.authenticate("nonuser", "password"))

    def test_wrong_password(self):
        """Test that invalid password fails"""

        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))

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

    def test_remove_favorite(self):
        """Test removing favorite"""
        
        # Test user should have one favorite
        self.assertEqual(len(self.u1.favorites), 1)

        Favorites.query.filter_by(hero_id=self.hid1, user_id=self.uid1).delete()
        db.session.commit()

        # Test user should now have 0 favorites
        self.assertEqual(len(self.u1.favorites), 0)
    
    def test_favorite_nonuser(self):
        """Test adding a favorite as a non-user"""

        # User ID that doesn't exist
        invalid_uid = 123
        
        fav_test = Favorites(user_id=invalid_uid, hero_id=self.hid2)
        
        # Should not be an instance as the user_id does not exist
        self.assertNotIsInstance(fav_test.user, User)