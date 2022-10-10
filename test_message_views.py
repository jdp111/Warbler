"""Message View tests."""

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app, CURR_USER_KEY

db.create_all()

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
                                    image_url=None,
                                    loc = None
                                    )

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


    def test_like_msg(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        c.post("/messages/new", data={"text": "Hello"})
        message = Message.query.one()
        resp = c.post(f"/users/add_like/{message.id}")

        self.assertEqual(resp.status_code,302)
        
        like = Likes.query.one()

        self.assertEqual(like.user_id, sess[CURR_USER_KEY])

    def test_view_msg(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        c.post("/messages/new", data={"text": "Hello"})
        message = Message.query.one()

        resp = c.get(f"/messages/{message.id}")

        self.assertEqual(resp.status_code,200)

        resp = c.get(f"/messages/{message.id}").get_data(as_text=True)

        self.assertIn("<div class='message-area'>",resp)

    def test_delete_msg(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
        c.post("/messages/new", data={"text": "Hello"})
        message = Message.query.one()

        resp = c.post(f"/messages/{message.id}/delete")

        self.assertEqual(resp.status_code,302)

        self.assertEqual(None,Message.query.one_or_none())

    def test_home(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
    
        c.post("/messages/new", data={"text": "Hello"})
        message = Message.query.one()
        
        resp = c.get("/").get_data(as_text=True)
        self.assertIn(message.text,resp)

        resp = c.get("/")

        self.assertEqual(resp.status_code,200)
