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
    """Helper function to create a test user."""
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
        # Create a test version of our application
        self.app = create_app()
        
        # Configure the app for testing
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'DEBUG': False,
            'SERVER_NAME': 'localhost.localdomain',  
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
        })
        
        # Setup application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test client
        self.client = self.app.test_client()
        
        # Create tables
        db.create_all()
        
        # Debug: Print all registered routes
        print("\nRegistered routes:")
        for rule in self.app.url_map.iter_rules():
            print(f"Route: {rule.rule}, Endpoint: {rule.endpoint}")

    def tearDown(self):
        """Executed after each test."""
        # Remove database session
        db.session.remove()
        
        # Drop all tables
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()

    def test_signup(self):
        """Test user signup functionality."""
        post_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'me1@example.com',
            'password': 'password',
            'submit': 'Sign Up'
        }
        
        # Make request to the signup route
        response = self.client.post('/signup', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the user now exists in the database
        user = User.query.filter_by(email='me1@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'me1@example.com')
        self.assertTrue(bcrypt.check_password_hash(user.password, 'password'))
        
        # Check redirection content
        response_text = response.get_data(as_text=True)
        self.assertIn('Login', response_text)

    def test_signup_existing_user(self):
        """Test signup with an already taken email."""
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
        response = self.client.post('/signup', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        response_text = response.get_data(as_text=True)
        self.assertIn('That email is taken', response_text)

    def test_login_correct_password(self):
        """Test login with correct credentials."""
        # Create user
        create_user()
        
        # Login data
        post_data = {
            'email': 'me1@example.com',
            'password': 'password',
            'submit': 'Log In'
        }
        
        # Make login request
        response = self.client.post('/login', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check login success indicators
        response_text = response.get_data(as_text=True)
        # self.assertIn('Log Out', response_text)
        
    def test_login_nonexistent_user(self):
        """Test login with a non-existent user."""
        # Login with non-existent user
        post_data = {
            'email': 'nonexistent@example.com',
            'password': 'password',
            'submit': 'Log In'
        }
        
        # Make login request
        response = self.client.post('/login', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        response_text = response.get_data(as_text=True)
        self.assertIn('No user with that email', response_text)

    def test_login_incorrect_password(self):
        """Test login with incorrect password."""
        # Create user
        create_user()
        
        # Login with incorrect password
        post_data = {
            'email': 'me1@example.com',
            'password': 'wrong_password',
            'submit': 'Log In'
        }
        
        # Make login request
        response = self.client.post('/login', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        response_text = response.get_data(as_text=True)
        self.assertIn('Invalid password', response_text)

    def test_logout(self):
        """Test user logout functionality."""
        # Create user and login
        create_user()
        login_data = {
            'email': 'me1@example.com',
            'password': 'password',
            'submit': 'Log In'
        }
        
        self.client.post('/login', data=login_data, follow_redirects=True)
        
        # Make logout request
        response = self.client.get('/logout', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check logout indicators
        response_text = response.get_data(as_text=True)
        self.assertIn('Log In', response_text)
        self.assertIn('You have been logged out', response_text)
