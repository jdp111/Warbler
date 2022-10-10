"""User model tests."""

import os
from unittest import TestCase
from models import db, User, Message, Follows
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        message = Message(
            text = "test message", 
            user_id = u.id
        )

        self.assertFalse(not message)

        db.session.add(message)
        db.session.commit()

        self.assertEqual(u.id, message.user.id)

