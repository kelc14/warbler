"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


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


class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id
        self.user_messages = user.messages

        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""
        # no messages before we add one
        self.assertEqual(len(self.user_messages), 0)

        m = Message(
            text="My first message.",
            user_id= self.user_id
        )

        db.session.add(m)
        db.session.commit()

        user = User.query.get(self.user_id)

        # User should have one message updated in database
        self.assertEqual(len(user.messages), 1)

    def test_message_repr(self):
        """Does the repr display properly"""

        m = Message(
            text="My second message.",
            user_id= self.user_id
        )

        db.session.add(m)
        db.session.commit()

        # Message __repr__ should display when message called (as string) with text in ex. 1 and using hard coded __repr__ in ex 2
        self.assertEqual(str(m), f'<Message {m.id}>')
        self.assertEqual(str(m.__repr__), f'<bound method Model.__repr__ of <Message {m.id}>>')
