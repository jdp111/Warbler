"""User View tests."""

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app, CURR_USER_KEY

db.drop_all()
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

    def test_user_signup(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get('/signup').get_data(as_text=True)

        self.assertIn( "<h2 class='join-message'>Join Warbler today.</h2>",resp)

        c.post("/signup", data = {"username":"username",
            "password":"password", 
            "email":"test@test.test", 
            "image_url":None,
            "location" : None
            })

        user = User.query.filter(User.username == "username").one()

        self.assertEqual(user.email, "test@test.test")

    
    def test_user_logout_login(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        resp = c.post('login', data={"username":"testuser", "password":"testuser"})
        self.assertEqual(resp.status_code,302)
        
        resp = c.post('login', data={"username":"username", "password":"password"})
        self.assertEqual(resp.status_code,200)


        
        resp = c.get('/logout')
        self.assertEqual(resp.status_code, 302)

        

    def test_users_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        c.post("/signup", data = {"username":"newUsername",
            "password":"password", 
            "email":"test@test.test", 
            "image_url":None,
            "location" : None
            })
        
        resp = c.get('/users')
        self.assertEqual(resp.status_code,200)

        html = resp.get_data(as_text=True)
        self.assertIn("newUsername",html)

        resp = c.get('/users?q=newU').get_data(as_text=True)
        self.assertIn("newUsername",resp)


    def test_show_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        c.post("/signup", data = {"username":"newUsername",
            "password":"password", 
            "email":"test@test.test", 
            "image_url":None,
            "location" : None
            })
        
        user = User.query.filter(User.username == "newUsername").one()

        resp = c.get(f"/users/{user.id}")

        self.assertEqual(resp.status_code,200)
        self.assertIn(user.username, resp.get_data(as_text=True))

    
    def test_follow_followed(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
        u1 = User(
            email = "test1@test1.com",
            username="user1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email = "test2@test2.com",
            username="user2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1 = User.query.filter(User.username == "user1").one()
        u2 = User.query.filter(User.username == "user2").one()

        resp = c.post(f"users/follow/{u1.id}",follow_redirects=True)
        self.assertIn("col-lg-4 col-md-6 col-12", resp.get_data(as_text=True))

        resp = c.get(f"/users/{sess[CURR_USER_KEY]}/following")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code,200)
        self.assertIn("user1",html)
        self.assertNotIn("user2",html)


        
    def test_unfollow_followed(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
            
            c.post('/login',data = {"username":"testuser","password":"testuser"})
            
            u1 = User(
                email = "tdwqw@test.com",
                username="user3",
                password="HASHED_PASSWORD"
            )
            db.session.add(u1)
            db.session.commit()

            u2 = User(
                email = "twfefe@test.com",
                username="user4",
                password="HASHED_PASSWORD"
            )
            db.session.add(u2)
            db.session.commit()

            c.post(f"/users/follow/8")
            c.post(f"/users/follow/9")
            resp = c.post(f"/users/stop-following/8",follow_redirects=True)
            self.assertIn("col-lg-4 col-md-6 col-12", resp.get_data(as_text=True))

            resp = c.get(f"/users/{sess[CURR_USER_KEY]}/following")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code,200)
            self.assertNotIn("user3",html)
            self.assertIn("user4",html)


    def test_followed_by(self):
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id

            followed = User.query.filter(User.username=="testuser").one()
            print(followed.id)

            c.post('/login',data = {"username":"newUsername","password":"password"})
            c.post(f"/users/follow/{followed.id}")
            
            resp = c.get(f"/users/{followed.id}/followers")
            html = resp.get_data(as_text=True)

            self.assertIn("testuser",html)
