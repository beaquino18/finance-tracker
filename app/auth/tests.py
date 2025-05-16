# app/auth/tests.py
import os
from unittest import TestCase
from flask import Flask
from app.extensions import db, bcrypt
from app.models import User
from app import create_app
from app.config import Config

"""
Run these tests with the command:
python -m unittest app.auth.tests
"""

#################################################
# Setup
#################################################

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(
        first_name='Test',
        last_name='User',
        email='me1@example.com',
        password=password_hash
    )
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        self.app = create_app()
        
        # Print all registered rules to debug
        with self.app.app_context():
            print("Registered URLs:")
            for rule in self.app.url_map.iter_rules():
                print(f"{rule.endpoint}: {rule.rule}")
        
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['DEBUG'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    # Clean up any resources that were allocated during the test, resets the state
    def tearDown(self):
        """Executed after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup(self):
        with self.app.app_context():
            post_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'me1@example.com',
                'password': 'password',
                'submit': 'Sign Up'
            }
            self.client.post('/auth/signup', data=post_data, follow_redirects=True)
            
            # Check that the user now exists in the database
            user = User.query.filter_by(email='me1@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'me1@example.com')
            self.assertTrue(bcrypt.check_password_hash(user.password, 'password'))

    def test_signup_existing_user(self):
        with self.app.app_context():
            # Create a user with email 'me1@example.com'
            create_user()
            
            # Try to create another user with the same email
            post_data = {
                'first_name': 'Another',
                'last_name': 'User',
                'email': 'me1@example.com',
                'password': 'password',
                'submit': 'Sign Up'
            }
            
            # Make the post request
            response = self.client.post('/auth/signup', data=post_data, follow_redirects=True)
            
            # Check that the response status is 200 (OK)
            self.assertEqual(response.status_code, 200)
            
            # Check that the form is displayed again with an error message
            response_text = response.get_data(as_text=True)
            
            # Check that the response contains an error message
            self.assertIn('That email is taken. Please choose a different one.', response_text)

    def test_login_correct_password(self):
        with self.app.app_context():
            create_user()
            
            post_data = {
                'email': 'me1@example.com',
                'password': 'password',
                'submit': 'Log In'
            }
            
            # Make the POST request to the login route
            response = self.client.post('/auth/login', data=post_data, follow_redirects=True)
            
            #Check if response status is 200
            self.assertEqual(response.status_code, 200)
            
            # Check that the response includes elements indicating successful login
            response_text = response.get_data(as_text=True)
            
            # Check for things that would indicate a successful login
            self.assertIn('Log Out', response_text)
            
    def test_login_nonexistent_user(self):
        with self.app.app_context():
            # Login with non-existent user
            post_data = {
                'email': 'nonexistent@example.com',
                'password': 'password',
                'submit': 'Log In'
            }
            
            # Make the POST request to login page
            response = self.client.post('/auth/login', data=post_data, follow_redirects=True)
            
            # Check if response is 200
            self.assertEqual(response.status_code, 200)
            
            # Check that the form is displayed again with an error message
            response_text = response.get_data(as_text=True)
            
            # Check that the response contains an error
            self.assertIn('No user with that email. Please try again.', response_text)

    def test_login_incorrect_password(self):
        with self.app.app_context():
            # Login with incorrect password
            create_user()
            post_data = {
                'email': 'me1@example.com',
                'password': 'password123',
                'submit': 'Log In'
            }
            
            # Make the POST request to the login route
            response = self.client.post('/auth/login', data=post_data, follow_redirects=True)
            
            # Check if the response returns 200
            self.assertEqual(response.status_code, 200)
            
            # Check that the form is displayed again with an error message
            response_text = response.get_data(as_text=True)
            
            # Check that the response contains an error
            self.assertIn('Password doesn&#39;t match. Please try again', response_text)

    def test_logout(self):
        with self.app.app_context():
            create_user()
            login_data = {
                'email': 'me1@example.com',
                'password': 'password',
                'submit': 'Log In'
            }
            
            self.client.post('/auth/login', data=login_data, follow_redirects=True)
            
            response = self.client.get('/auth/logout', follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            response_text = response.get_data(as_text=True)
            
            self.assertIn('Log In', response_text)
            self.assertNotIn('Log Out', response_text)
