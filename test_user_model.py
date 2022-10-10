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

    def test_following(self):
        u1 = User(
            email = "test1@test1.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email = "test2@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertFalse(u2.is_followed_by(u1))
        self.assertFalse(u1.is_following(u2))

        f = Follows(
            user_being_followed_id = u2.id,
            user_following_id = u1.id
        )
        db.session.add(f)
        db.session.commit()

        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.is_following(u2))

    def test_userSignup(self):
        newUser = User.signup(
            username = "cool",
            email="sump@sump.cool",
            password = "password",
            image_url = "",
            loc=None
        )
        
        self.assertTrue(newUser.email)

        db.session.add(newUser)
        db.session.commit()

    


    def test_userAuth(self):

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url = "",
            loc=None
        )
        print(u.id)
        db.session.add(u)
        db.session.commit()

        valid = User.authenticate(username = "testuser",password = "HASHED_PASSWORD")

        self.assertEqual(valid.username,"testuser")

        invalid = User.authenticate("notauser","HASHED_PASSWORD")

        self.assertFalse(invalid)

        invalid = User.authenticate("testuser","password")

        self.assertFalse(invalid)