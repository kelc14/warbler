"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    # logout and try the same thing
    def test_add_message_not_logged_in(self):
        """Can use add a message when we are not logged in ?"""

        with self.client as c:    
            
            resp2 = c.post("/messages/new")
                # Make sure it gives redirect code 302 since we are not logged in 
            self.assertEqual(resp2.status_code, 302)
                
    def test_add_message_not_logged_in_redirect(self):
        """Test the redirect that follows attempting to add a message when not logged in """
        with self.client as c:
            resp = c.post('/messages/new', follow_redirects=True)

            html = resp.get_data(as_text=True)
            ## test that we are redirected successfully and that our flash message of access unauthorized is displayed:
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Access unauthorized.', html)
    
    def test_delete_message(self):
        """Can use delete a message when logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # now logged in, create message before request

            msg = Message(text="This is a test message", user_id=self.testuser.id)
            db.session.add(msg)
            db.session.commit()

            resp = c.post(f"/messages/{msg.id}/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # msg with this id does not exist
            self.assertFalse(Message.query.get(msg.id))

            # logout and try the same thing
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None
            
            msg2 = Message(text="This is a test message", user_id=self.testuser.id)
            db.session.add(msg2)
            db.session.commit()

            resp2 = c.post(f"/messages/{msg2.id}/delete")

            # Make sure it gives redirect code 302 since we are not logged in 
            self.assertEqual(resp2.status_code, 302)
            # msg2 should still exist
            self.assertTrue(Message.query.get(msg2.id))

    def test_add_message_as_wrong_user(self):
        """When you’re logged in, are you prohibiting from adding a message as another user"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            user2 = User(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD"
            )
            db.session.add(user2)
            db.session.commit()

            resp = c.post("/messages/new", data={"text": "Hello", "user_id":user2.id})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            #msg id should NOT match the user we are attempting to create a message as
            msg = Message.query.one()
            self.assertNotEqual(msg.user_id, user2.id)
        
    
    
    
    
    def test_view_follower(self):
        """When you’re logged in, can you see the follower / following pages for any user?"""

        with self.client as c:
            # first make sure user is logged in (saved in session)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user2 = User(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD"
            )

            user3 = User(
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD"
            )
            db.session.add_all([user2, user3])
            db.session.commit()

            #create the follow (testuser followed by user2)

            f = Follows(user_being_followed_id=self.testuser.id,
                        user_following_id=user2.id)
            db.session.add(f)
            db.session.commit()

            #user 2 should be on follows pg, but not user 3
            # now load the page
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)

            # Make sure it loads OK
            self.assertEqual(resp.status_code, 200)

            self.assertIn('testuser2', html)
            self.assertNotIn('testuser3', html)

            #can we see the follower page for user 2 ? Should not be any users in html. 
            resp2 = c.get(f"/users/{user2.id}/followers")
            html2 = resp2.get_data(as_text=True)

            # Make sure it loads OK
            self.assertEqual(resp2.status_code, 200)

            self.assertIn('testuser2', html2)
            self.assertNotIn('testuser3', html2)


            #now log out and instead of 200 status code we should get a redirect to homepage

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None
            
            resp3 = c.get(f"/users/{user2.id}/followers")

            # Make sure it gives redirect code 302
            self.assertEqual(resp3.status_code, 302)
            
    def test_view_following(self):
        """When you’re logged in, can you see the following pages for any user?"""

        with self.client as c:
            # first make sure user is logged in (saved in session)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user2 = User(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD"
            )

            user3 = User(
                email="test3@test.com",
                username="testuser3",
                password="HASHED_PASSWORD"
            )
            db.session.add_all([user2, user3])
            db.session.commit()

            #create the follow (testuser following  user2)

            f = Follows(user_being_followed_id=user2.id,
                        user_following_id=self.testuser.id)
            db.session.add(f)
            db.session.commit()

            #user 2 should be on following pg, but not user 3
            # now load the page
            resp = c.get(f"/users/{self.testuser.id}/following")
            html = resp.get_data(as_text=True)

            # Make sure it loads OK
            self.assertEqual(resp.status_code, 200)

            self.assertIn('testuser2', html)
            self.assertNotIn('testuser3', html)


            #can we see the following page for user 2 ? Should not be any users in html. 
            resp2 = c.get(f"/users/{user2.id}/following")
            html2 = resp2.get_data(as_text=True)

            # Make sure it loads OK
            self.assertEqual(resp2.status_code, 200)

            self.assertIn('testuser2', html2)
            self.assertNotIn('testuser3', html2)


            #now log out and instead of 200 status code we should get a redirect to homepage

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = None
            
            resp3 = c.get(f"/users/{user2.id}/following")

            # Make sure it gives redirect code 302
            self.assertEqual(resp3.status_code, 302)


            
