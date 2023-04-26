"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()
        
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.add_all([self.testuser, self.testuser2])
        db.session.commit()
    
    def tearDown(self):
        """Clean up any fouled transaction"""

        db.session.rollback()

    def test_view_user(self):
        """Can we view list of all users?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # both users should appear
            self.assertIn('@testuser', html)
            self.assertIn('@testuser2', html)

    def test_view_user_profile(self):
        """Can we view profile of a single user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # user 1 should appear in user 1 profile
            self.assertIn('@testuser', html)
            # user 2 should not appear in user 1 profile
            self.assertNotIn('@testuser2', html)

    def test_view_profile(self):
        """Can we view profile for a logged in user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
            # user 2 should not appear in user 1 profile
            self.assertNotIn('testuser2', html)



    def test_view_edit_profile(self):
        """Can we view profile edit form for logged in user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)
            # form should be appearing
            self.assertIn('<button class="btn btn-success">Edit this user!</button>', html)
    def test_edit_profile(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/users/profile", data = {'username': 'testuser12345'})

            self.assertEqual(resp.status_code, 302)
            # self.assertIn('testuser', html)
            # # form should be appearing
            # self.assertIn('<button cl

    def test_edit_profile_redirect(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/users/profile", data = {
                'username': 'testuser12345', 
                'password':"testuser"}, 
                follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # new username appears
            self.assertIn('testuser12345', html)

    def test_delete_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post('/users/delete')

            self.assertEqual(resp.status_code, 302)
    
    def test_delete_user_redirect(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post('/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)


            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sign me up!', html)
    
    def test_add_follow(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User.query.offset(1).first()
            resp = c.post(f'/users/follow/{user2.id}')

            self.assertEqual(resp.status_code, 302)

    def test_add_follow_redirect(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User.query.offset(1).first()
            resp = c.post(f'/users/follow/{user2.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            # now following user 2, so they should show up on the page.
            self.assertIn('@testuser2', html)


           
            
            



