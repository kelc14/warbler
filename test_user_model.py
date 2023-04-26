"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Does the repr display properly"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User __repr__ should display when user called (as string) with text in ex. 1 and using hard coded __repr__ in ex 2
        self.assertEqual(str(u), f'<User #{u.id}: testuser, test@test.com>')
        self.assertEqual(str(u.__repr__), f'<bound method User.__repr__ of <User #{u.id}: testuser, test@test.com>>')

    def test_is_following(self):
        """Does is_following successfully 
        detect when user1 is following user2?
        
        and NOT following user3 """

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

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
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        #create the follow (user 1 follows user 2)

        f = Follows(user_being_followed_id=user2.id,
                    user_following_id=user1.id)
        db.session.add(f)
        db.session.commit()

        # test that user 1 is follwing user 2
        self.assertEqual(user1.is_following(user2), 1)
        # test that user 1 is NOT following user 3
        self.assertFalse(user1.is_following(user3))

    def test_is_followed_by(self):
        """Does is_followed_by successfully 
        detect when user1 is followed by user2?
        
        and NOT followed by user3 """

        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

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
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        #create the follow (user 2 follows user 1)

        f = Follows(user_being_followed_id=user1.id,
                    user_following_id=user2.id)
        db.session.add(f)
        db.session.commit()

        # test that user 1 is follwing user 2
        self.assertEqual(user1.is_followed_by(user2), 1)
        # test that user 1 is NOT following user 3
        self.assertFalse(user1.is_followed_by(user3))

    def test_user_signup(self):
        """Does User.signup create a new user given valid credentials :
            (username, 
            email, 
            password, 
            image_url (optional))
        """

        user = User.signup(username="user123", 
                    password="hashed_password", email="email@gmail.com", 
                    image_url="warbler")
        
        self.assertEqual(user.username, 'user123')
        self.assertEqual(user.email, 'email@gmail.com')
        self.assertEqual(user.image_url, 'warbler')

        #test this fails when missing image url
        with self.assertRaises(TypeError):
            User.signup(username="user10000", password="password", email="email")

    def test_user_authenticate(self):
        """Does user.authenticate return a user when given a valid username and password? """

        user = User.signup(username="user123", 
                    password="hashed_password", email="email@gmail.com", 
                    image_url="warbler")
        
        returned_user = User.authenticate(username="user123", password="hashed_password")

        # test that returned user from authenticate matches the user with those credentials
        self.assertEqual(user, returned_user)


        # test that no user is returned if incorrect password
        failed_returned_user = User.authenticate(username="user123", password="wrong_password")
        self.assertNotEqual(user, failed_returned_user)
        #returns false
        self.assertFalse(failed_returned_user)

        # test that no user is returned if incorrect username
        failed_returned_user2 = User.authenticate(username="user1111111111", password="hashed_password")
        self.assertNotEqual(user, failed_returned_user2)
        #returns false
        self.assertFalse(failed_returned_user2)

    

        

