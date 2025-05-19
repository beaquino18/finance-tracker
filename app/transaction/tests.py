# app/transaction/tests.py
import os
import uuid
from unittest import TestCase
from datetime import date
from flask import Flask
from app.extensions import db, bcrypt
from app.models import User, Wallet, Category, Transaction, Label
from app import create_app
from app.enum import Color, CategoryIcon

"""
Run these tests with the command:
python -m unittest app.transaction.tests
"""

#################################################
# Setup
#################################################

def create_test_user():
    """Helper function to create a test user with a unique email."""
    # Generate a unique email for each test user
    unique_email = f"transaction_test_{uuid.uuid4().hex[:8]}@example.com"
    
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(
        first_name='Test',
        last_name='User',
        email=unique_email,
        password=password_hash
    )
    db.session.add(user)
    db.session.commit()
    return user

def create_test_wallet(user):
    """Helper function to create a test wallet."""
    wallet = Wallet(
        name='Test Wallet',
        balance=1000.00,
        color=Color.BLUE,
        is_active=True,
        user_id=user.id
    )
    db.session.add(wallet)
    db.session.commit()
    return wallet

def create_test_category(user):
    """Helper function to create a test category."""
    category = Category(
        name='Test Category',
        color=Color.GREEN,
        icon=CategoryIcon.DOLLAR_SIGN.value,
        user_id=user.id
    )
    db.session.add(category)
    db.session.commit()
    return category

def create_test_label(user):
    """Helper function to create a test label."""
    label = Label(
        name='Test Label',
        user_id=user.id
    )
    db.session.add(label)
    db.session.commit()
    return label

def create_test_transaction(user, wallet, category, label=None):
    """Helper function to create a test transaction."""
    transaction = Transaction(
        amount=100.00,
        description='Test Transaction',
        date=date.today(),
        is_expense=True,
        category_id=category.id,
        wallet_id=wallet.id,
        user_id=user.id
    )
    
    if label:
        transaction.labels.append(label)
    
    # Update wallet balance based on transaction
    if transaction.is_expense:
        wallet.balance -= transaction.amount
    else:
        wallet.balance += transaction.amount
    
    db.session.add(transaction)
    db.session.commit()
    return transaction

#################################################
# Tests
#################################################

class TransactionTests(TestCase):
    """Tests for transaction functionality."""

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
        
        # Create test user, wallet, category and label for transaction tests
        self.test_user = create_test_user()
        self.test_wallet = create_test_wallet(self.test_user)
        self.test_category = create_test_category(self.test_user)
        self.test_label = create_test_label(self.test_user)
        
        # Record initial wallet balance for assertions
        self.initial_wallet_balance = float(self.test_wallet.balance)
        
        # Login the test user
        self.client.post('/login', data={
            'email': self.test_user.email,  # Use the dynamically generated email
            'password': 'password',
            'submit': 'Log In'
        })

    def tearDown(self):
        """Executed after each test."""
        # Remove database session
        db.session.remove()
        
        # Drop all tables
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()

    def test_create_transaction_expense(self):
        """Test creating an expense transaction."""
        original_balance = float(self.test_wallet.balance)
        expense_amount = 50.00
        
        post_data = {
            'amount': expense_amount,
            'description': 'Test Expense',
            'date': date.today().strftime('%Y-%m-%d'),
            'is_expense': True,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id,
            'labels': []
        }
        
        # Make request to the transaction create route
        response = self.client.post('/transaction/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction exists in the database
        transaction = Transaction.query.filter_by(
            description='Test Expense',
            user_id=self.test_user.id
        ).first()
        
        # Verify transaction was created correctly
        self.assertIsNotNone(transaction)
        self.assertEqual(float(transaction.amount), expense_amount)
        self.assertEqual(transaction.description, 'Test Expense')
        self.assertTrue(transaction.is_expense)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Verify wallet balance was updated correctly
        self.assertEqual(float(self.test_wallet.balance), original_balance - expense_amount)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('New Transaction created successfully', response_text)

    def test_create_transaction_income(self):
        """Test creating an income transaction."""
        original_balance = float(self.test_wallet.balance)
        income_amount = 75.50
        
        post_data = {
            'amount': income_amount,
            'description': 'Test Income',
            'date': date.today().strftime('%Y-%m-%d'),
            'is_expense': False,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id,
            'labels': []
        }
        
        # Make request to the transaction create route
        response = self.client.post('/transaction/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction exists in the database
        transaction = Transaction.query.filter_by(
            description='Test Income',
            user_id=self.test_user.id
        ).first()
        
        # Verify transaction was created correctly
        self.assertIsNotNone(transaction)
        self.assertEqual(float(transaction.amount), income_amount)
        self.assertFalse(transaction.is_expense)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Verify wallet balance was updated correctly
        self.assertEqual(float(self.test_wallet.balance), original_balance + income_amount)

    def test_create_transaction_with_labels(self):
        """Test creating a transaction with labels."""
        post_data = {
            'amount': 25.00,
            'description': 'Test with Labels',
            'date': date.today().strftime('%Y-%m-%d'),
            'is_expense': True,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id,
            'labels': [self.test_label.id]
        }
        
        # Make request to the transaction create route
        response = self.client.post('/transaction/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction exists in the database
        transaction = Transaction.query.filter_by(
            description='Test with Labels',
            user_id=self.test_user.id
        ).first()
        
        # Verify transaction was created correctly
        self.assertIsNotNone(transaction)
        
        # Check if label is attached to the transaction
        self.assertEqual(len(transaction.labels), 1)
        self.assertEqual(transaction.labels[0].id, self.test_label.id)

    def test_view_transaction_detail(self):
        """Test viewing transaction details."""
        # Create a transaction
        transaction = create_test_transaction(
            self.test_user, 
            self.test_wallet, 
            self.test_category, 
            self.test_label
        )
        
        # Make request to view transaction details
        response = self.client.get(f'/transaction/{transaction.id}')
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that transaction details are in the response
        response_text = response.get_data(as_text=True)
        self.assertIn('Test Transaction', response_text)
        self.assertIn('$100.00', response_text)
        self.assertIn('Expense', response_text)
        self.assertIn('Test Category', response_text)
        self.assertIn('Test Wallet', response_text)
        self.assertIn('Test Label', response_text)

    def test_update_transaction_amount(self):
        """Test updating a transaction's amount."""
        # Create a transaction
        transaction = create_test_transaction(
            self.test_user, 
            self.test_wallet, 
            self.test_category
        )
        
        original_wallet_balance = float(self.test_wallet.balance)
        new_amount = 75.00
        
        update_data = {
            'amount': new_amount,
            'description': transaction.description,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'is_expense': transaction.is_expense,
            'category_id': transaction.category_id,
            'wallet_id': transaction.wallet_id,
            'labels': []
        }
        
        # Make request to update the transaction
        response = self.client.post(
            f'/transaction/{transaction.id}/update',
            data=update_data,
            follow_redirects=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction was updated in the database
        updated_transaction = db.session.get(Transaction, transaction.id)
        self.assertEqual(float(updated_transaction.amount), new_amount)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Since original was 100.00 expense and new is 75.00 expense,
        # the wallet balance should increase by 25.00
        expected_balance = original_wallet_balance + (100.00 - 75.00)
        self.assertEqual(float(self.test_wallet.balance), expected_balance)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Transaction updated successfully', response_text)

    def test_update_transaction_type(self):
        """Test changing a transaction from expense to income."""
        # Create an expense transaction
        transaction = create_test_transaction(
            self.test_user, 
            self.test_wallet, 
            self.test_category
        )
        
        original_wallet_balance = float(self.test_wallet.balance)
        
        # Change from expense to income
        update_data = {
            'amount': transaction.amount,
            'description': transaction.description,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'is_expense': False,  # Changed from True to False
            'category_id': transaction.category_id,
            'wallet_id': transaction.wallet_id,
            'labels': []
        }
        
        # Make request to update the transaction
        response = self.client.post(
            f'/transaction/{transaction.id}/update',
            data=update_data,
            follow_redirects=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction type was updated
        updated_transaction = db.session.get(Transaction, transaction.id)
        self.assertFalse(updated_transaction.is_expense)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Since we're changing from expense to income, balance should increase by 2x amount
        # (undo expense + add income)
        expected_balance = original_wallet_balance + (float(transaction.amount) * 2)
        self.assertEqual(float(self.test_wallet.balance), expected_balance)

    def test_update_transaction_wallet(self):
        """Test changing a transaction's wallet."""
        # Create an expense transaction
        transaction = create_test_transaction(
            self.test_user, 
            self.test_wallet, 
            self.test_category
        )
        
        # Record original wallet balance
        original_wallet_balance = float(self.test_wallet.balance)
        
        # Create a second wallet
        second_wallet = Wallet(
            name='Second Wallet',
            balance=500.00,
            color=Color.RED,
            is_active=True,
            user_id=self.test_user.id
        )
        db.session.add(second_wallet)
        db.session.commit()
        
        # Update transaction to use second wallet
        update_data = {
            'amount': transaction.amount,
            'description': transaction.description,
            'date': transaction.date.strftime('%Y-%m-%d'),
            'is_expense': transaction.is_expense,
            'category_id': transaction.category_id,
            'wallet_id': second_wallet.id,  # Changed wallet
            'labels': []
        }
        
        # Make request to update the transaction
        response = self.client.post(
            f'/transaction/{transaction.id}/update',
            data=update_data,
            follow_redirects=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction wallet was updated
        updated_transaction = db.session.get(Transaction, transaction.id)
        self.assertEqual(updated_transaction.wallet_id, second_wallet.id)
        
        # Reload wallets to get updated balances
        db.session.refresh(self.test_wallet)
        db.session.refresh(second_wallet)
        
        # Original wallet should have had the expense removed (+100)
        self.assertEqual(float(self.test_wallet.balance), original_wallet_balance + 100.00)
        
        # Second wallet should have the expense added (-100)
        self.assertEqual(float(second_wallet.balance), 400.00)

    def test_delete_transaction_expense(self):
        """Test deleting an expense transaction."""
        # Create an expense transaction
        transaction = create_test_transaction(
            self.test_user, 
            self.test_wallet, 
            self.test_category
        )
        
        # Record original wallet balance
        original_wallet_balance = float(self.test_wallet.balance)
        
        # Make request to delete the transaction
        response = self.client.post(
            f'/transaction/{transaction.id}/delete',
            follow_redirects=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the transaction is deleted
        deleted_transaction = db.session.get(Transaction, transaction.id)
        self.assertIsNone(deleted_transaction)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Balance should have increased by the expense amount
        self.assertEqual(float(self.test_wallet.balance), original_wallet_balance + 100.00)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Transaction deleted successfully', response_text)

    def test_delete_transaction_income(self):
        """Test deleting an income transaction."""
        # Create an income transaction
        income_transaction = Transaction(
            amount=100.00,
            description='Test Income',
            date=date.today(),
            is_expense=False,  # Income
            category_id=self.test_category.id,
            wallet_id=self.test_wallet.id,
            user_id=self.test_user.id
        )
        
        # Update wallet balance
        self.test_wallet.balance += income_transaction.amount
        
        db.session.add(income_transaction)
        db.session.commit()
        
        # Record original wallet balance
        original_wallet_balance = float(self.test_wallet.balance)
        
        # Make request to delete the transaction
        response = self.client.post(
            f'/transaction/{income_transaction.id}/delete',
            follow_redirects=True
        )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Reload wallet to get updated balance
        db.session.refresh(self.test_wallet)
        
        # Balance should have decreased by the income amount
        self.assertEqual(float(self.test_wallet.balance), original_wallet_balance - 100.00)

    def test_access_other_user_transaction(self):
        """Test accessing another user's transaction."""
        # Create a second user with unique email
        second_user = User(
            first_name='Other',
            last_name='User',
            email=f"other_user_{uuid.uuid4().hex[:8]}@example.com",
            password=bcrypt.generate_password_hash('password').decode('utf-8')
        )
        db.session.add(second_user)
        db.session.commit()
        
        # Create wallet, category for second user
        second_wallet = create_test_wallet(second_user)
        second_category = create_test_category(second_user)
        
        # Create a transaction for second user
        other_transaction = create_test_transaction(
            second_user, 
            second_wallet, 
            second_category
        )
        
        # Try to access the second user's transaction
        response = self.client.get(f'/transaction/{other_transaction.id}', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check access denied message
        response_text = response.get_data(as_text=True)
        self.assertIn('Transaction not found or access denied', response_text)
        
        # Try to update the second user's transaction
        update_data = {
            'amount': 50.00,
            'description': 'Unauthorized Update',
            'date': date.today().strftime('%Y-%m-%d'),
            'is_expense': True,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id,
            'labels': []
        }
        
        response = self.client.post(
            f'/transaction/{other_transaction.id}/update',
            data=update_data,
            follow_redirects=True
        )
        
        # Check access denied message
        self.assertIn('Transaction not found or access denied', response.get_data(as_text=True))
        
        # Try to delete the second user's transaction
        response = self.client.post(
            f'/transaction/{other_transaction.id}/delete',
            follow_redirects=True
        )
        
        # Check access denied message
        self.assertIn('Transaction not found or access denied', response.get_data(as_text=True))
        
        # Verify the transaction still exists
        other_transaction = db.session.get(Transaction, other_transaction.id)
        self.assertIsNotNone(other_transaction)
