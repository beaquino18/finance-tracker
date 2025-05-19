# app/wallet/tests.py
import os
from unittest import TestCase
from flask import Flask
from app.extensions import db, bcrypt
from app.models import User, Wallet, Transaction, Budget
from app import create_app
from app.config import Config


"""
Run these tests with the command:
python -m unittest app.wallet.tests
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
        email='wallet_test@example.com',
        password=password_hash
    )
    db.session.add(user)
    db.session.commit()
    return user

def create_wallet(user):
    """Helper function to create a test wallet."""
    wallet = Wallet(
        name='Test Wallet',
        balance=1000.00,
        is_active=True,
        user_id=user.id
    )
    db.session.add(wallet)
    db.session.commit()
    return wallet

#################################################
# Tests
#################################################

class WalletTests(TestCase):
    """Tests for wallet functionality."""

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
        
        # Create test user
        self.test_user = create_user()
        
        # Login the test user
        login_data = {
            'email': 'wallet_test@example.com',
            'password': 'password',
            'submit': 'Log In'
        }
        self.client.post('/login', data=login_data, follow_redirects=True)

    def tearDown(self):
        """Executed after each test."""
        # Remove database session
        db.session.remove()
        
        # Drop all tables
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()

    def test_create_wallet(self):
        """Test wallet creation functionality."""
        post_data = {
            'name': 'New Test Wallet',
            'balance': 500.00,
            'is_active': True
        }
        
        # Make request to the wallet create route
        response = self.client.post('/wallet/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the wallet now exists in the database
        wallet = Wallet.query.filter_by(
            name='New Test Wallet',
            user_id=self.test_user.id
        ).first()
        
        self.assertIsNotNone(wallet)
        self.assertEqual(float(wallet.balance), 500.00)
        self.assertTrue(wallet.is_active)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('New Wallet was created successfully', response_text)

    def test_update_wallet(self):
        """Test wallet update functionality."""
        # Create a wallet to update
        wallet = create_wallet(self.test_user)
        
        # Update data
        update_data = {
            'name': 'Updated Wallet Name',
            'balance': 1500.00,
            'is_active': '0'  # Use string '0' for false in form data
        }
        
        # Make request to update the wallet
        response = self.client.post(f'/wallet/{wallet.id}/update', 
                                    data=update_data, 
                                    follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Verify the wallet was updated
        updated_wallet = db.session.get(Wallet, wallet.id)  # Use db.session.get instead of .query.get
        self.assertEqual(updated_wallet.name, 'Updated Wallet Name')
        self.assertEqual(float(updated_wallet.balance), 1500.00)
        self.assertTrue(updated_wallet.is_active)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Wallet updated successfully', response_text)

    def test_delete_wallet(self):
        """Test wallet deletion functionality."""
        # Create a wallet to delete
        wallet = create_wallet(self.test_user)
        
        # Make request to delete the wallet
        response = self.client.post(f'/wallet/{wallet.id}/delete', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Verify the wallet was deleted
        deleted_wallet = db.session.get(Wallet, wallet.id)  # Use db.session.get instead of .query.get
        self.assertIsNone(deleted_wallet)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Wallet deleted successfully', response_text)


    def test_wallet_detail(self):
        """Test accessing wallet detail page."""
        # Create a wallet
        wallet = create_wallet(self.test_user)
        
        # Make request to the wallet detail route
        response = self.client.get(f'/wallet/{wallet.id}')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that wallet details are displayed
        response_text = response.get_data(as_text=True)
        self.assertIn(wallet.name, response_text)
        self.assertIn(f"${wallet.balance:.2f}", response_text)
        
        # Check for sections
        self.assertIn('Transactions', response_text)
        self.assertIn('Budgets', response_text)

    def test_access_other_user_wallet(self):
        """Test accessing another user's wallet."""
        # Create another user with a wallet
        other_user = User(
            first_name='Other',
            last_name='User',
            email='other@example.com',
            password=bcrypt.generate_password_hash('password').decode('utf-8')
        )
        db.session.add(other_user)
        db.session.commit()
        
        other_wallet = Wallet(
            name='Other Wallet',
            balance=2000.00,
            is_active=True,
            user_id=other_user.id
        )
        db.session.add(other_wallet)
        db.session.commit()
        
        # Try to access the other user's wallet
        response = self.client.get(f'/wallet/{other_wallet.id}', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check access denied message
        response_text = response.get_data(as_text=True)
        self.assertIn('Wallet not found or access denied', response_text)
        
        # Try to update the other user's wallet
        update_data = {
            'name': 'Hacked Wallet',
            'balance': 0.00,
            'is_active': False
        }
        
        response = self.client.post(f'/wallet/{other_wallet.id}/update', 
                                    data=update_data,
                                    follow_redirects=True)
        
        # Check that the wallet was not updated and access denied
        self.assertIn('Wallet not found or access denied', response.get_data(as_text=True))
        
        # Try to delete the other user's wallet
        response = self.client.post(f'/wallet/{other_wallet.id}/delete', follow_redirects=True)
        
        # Check that the wallet was not deleted and access denied
        self.assertIn('Wallet not found or access denied', response.get_data(as_text=True))
        
        # Verify the wallet still exists and was not modified
        other_wallet = db.session.get(Wallet, other_wallet.id)  # Use db.session.get instead of .query.get
        self.assertIsNotNone(other_wallet)
        self.assertEqual(other_wallet.name, 'Other Wallet')
