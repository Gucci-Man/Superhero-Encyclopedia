"""User View tests"""

# run these tests like:
#
#    python3 -m unittest test_user_views.py

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

    def test_info_page(self):
        """Test that the main superhero encyclopedia page shows when logged in"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id
            
            test_uid = self.u1.id
            resp = c.get("/superheros")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="cell-name">Black Widow</span>', html)
            self.assertEqual(sess[CURR_USER_KEY], test_uid)

    def test_invalid_user_page(self):
        """Test that invalid user will be unable to access website"""

        with app.test_client() as c:
            resp = c.get("/superheros", follow_redirects=True)
            html = resp.get_data(as_text=True)

            # Should redirect back to login page and show flash message
            self.assertEqual(resp.status_code, 200)
            self.assertIn('>Access unauthorized.</div>', html)

    def test_user_profile(self):
        """Test to view user profile when logged in"""
        
        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            test_uid = self.u1.id 
            resp = c.get(f"/users/{test_uid}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<li>Username: test1</li>', html)

    def test_user_favorites(self):
        """Test to view user's favorites page"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            
            resp = c.get("/users/favorites")
            html = resp.get_data(as_text=True)

            # Test user favorite should be groot
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h3>Superhero: Groot</h3>', html)

    def test_add_favorite(self):
        """Test adding a favorite superhero"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # Test hero id is Nick Fury
            test_hid = self.hid2

            resp = c.post(f"/superheros/{test_hid}/fav", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # Test user should now have 2 favorites, originally had 1 favorite
            favs = Favorites.query.filter(Favorites.user_id==self.u1.id).all()
            self.assertEqual(len(favs), 2)
            self.assertEqual(favs[1].user_id, self.u1.id)
            self.assertEqual(favs[1].hero_id, test_hid)

    def test_remove_favorite(self):
        """Test removing a favorite superhero"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            # Test hero to un-favorite is Groot, from SetUp method
            test_hid = self.hid1   

            resp = c.post(f"/superheros/{test_hid}/fav", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # Test user should now have 0 favorites
            favs = Favorites.query.filter(Favorites.user_id==self.u1.id).all()
            self.assertEqual(len(favs), 0)