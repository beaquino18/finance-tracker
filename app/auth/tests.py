import os
from unittest import TestCase
from app.extensions import app, db, bcrypt
from app.models import User

"""
Run these tests with the command:
python -m unittest app.auth.tests
"""

#################################################
# Setup
#################################################

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        
        db.drop_all()
        db.create_all()

    # Clean up any resources that were allocated during the test, resets the state
    def tearDown(self):
        """Executed after each test."""
        db.session.remove()
        db.drop_all()

    def test_signup(self):
        post_data = {
            'username': 'me1',
            'password': 'password',
            'submit': 'Sign Up'
        }
        self.app.post('/signup', data=post_data, follow_redirects=True)
        
        db.session.commit()
        
        # Check that the user now exists in the database
        user = User.query.filter_by(username='me1').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'me1')  # Changed from 'me2' to 'me1'
        self.assertTrue(bcrypt.check_password_hash(user.password, 'password'))

    def test_signup_existing_user(self):
        # Create a user with username 'me1'
        create_user()
        
        # Try to create another user with the same username
        post_data = {
            'username': 'me1',
            'password': 'password',
            'submit': 'Sign Up'
        }
        
        # Make the post request
        response = self.app.post('/signup', data=post_data, follow_redirects=True)
        
        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is displayed again with an error message
        response_text = response.get_data(as_text=True)
        
        # Check that the response contains an error message
        self.assertIn('That username is taken. Please choose a different one.', response_text)
        

    def test_login_correct_password(self):
        create_user()
        
        post_data = {
            'username': 'me1',
            'password': 'password',
            'submit': 'Log In'
        }
        
        # Make the POST request to the login route
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        
        #Check if response status is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the response includes elements indicating successful login
        response_text = response.get_data(as_text=True)
        
        # Check for things that would indicate a successful login
        # TODO
        # self.assertIn('Create Book', response_text)
        # self.assertIn('Create Author', response_text)
        # self.assertIn('Create Genre', response_text)
        self.assertIn('Log Out', response_text)
        
        
    def test_login_nonexistent_user(self):
        # Login with non-existent user
        post_data = {
            'username': 'me2',
            'password': 'password',
            'submit': 'Log In'
        }
        
        # Make the POST request to login page
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        
        # Check if response is 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is displayed again with an error message
        response_text = response.get_data(as_text=True)
        
        # Check that the response contains an error
        self.assertIn('No user with that username. Please try again.', response_text)


    def test_login_incorrect_password(self):
        # Login with incorrect password
        create_user()
        post_data = {
            'username': 'me1',
            'password': 'password123',
            'submit': 'Log In'
        }
        
        # Make the POST request to the login route
        response = self.app.post('/login', data=post_data, follow_redirects=True)
        
        # Check if the response returns 200
        self.assertEqual(response.status_code, 200)
        
        # Check that the form is displayed again with an error message
        response_text = response.get_data(as_text=True)
        
        # Chec that the response contains an error
        self.assertIn('Password doesn&#39;t match. Please try again', response_text)

    def test_logout(self):
        create_user()
        login_data = {
            'username': 'me1',
            'password': 'password',
            'submit': 'Log In'
        }
        
        self.app.post('/login', data=login_data, follow_redirects=True)
        
        response = self.app.get('/logout', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        response_text = response.get_data(as_text=True)
        
        self.assertIn('Log In', response_text)
        self.assertNotIn('Log Out', response_text)
