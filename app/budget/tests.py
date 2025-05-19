# app/budget/tests.py
import os
from unittest import TestCase
from flask import Flask
from app.extensions import db, bcrypt
from app.models import User, Wallet, Category, Budget
from app import create_app
from app.enum import Color, MonthList, CategoryIcon

"""
Run these tests with the command:
python -m unittest app.budget.tests
"""

#################################################
# Setup
#################################################

def create_test_user():
    """Helper function to create a test user."""
    # Check if the user already exists
    existing_user = User.query.filter_by(email='budget_test@example.com').first()
    if existing_user:
        return existing_user
        
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(
        first_name='Test',
        last_name='User',
        email='budget_test@example.com',
        password=password_hash
    )
    db.session.add(user)
    db.session.commit()
    return user

def create_test_wallet(user):
    """Helper function to create a test wallet."""
    # Check if the wallet already exists
    existing_wallet = Wallet.query.filter_by(
        name='Test Wallet',
        user_id=user.id
    ).first()
    if existing_wallet:
        return existing_wallet
        
    wallet = Wallet(
        name='Test Wallet',
        balance=1000.00,
        is_active=True,
        user_id=user.id
    )
    db.session.add(wallet)
    db.session.commit()
    return wallet

def create_test_category(user):
    """Helper function to create a test category."""
    # Check if the category already exists
    existing_category = Category.query.filter_by(
        name='Test Category',
        user_id=user.id
    ).first()
    if existing_category:
        return existing_category
        
    category = Category(
        name='Test Category',
        color=Color.GREEN,
        icon=CategoryIcon.DOLLAR_SIGN.value,
        user_id=user.id
    )
    db.session.add(category)
    db.session.commit()
    return category

def create_test_budget(user, wallet, category):
    """Helper function to create a test budget."""
    budget = Budget(
        amount=500.00,
        month=MonthList.JAN,
        year=2025,
        category_id=category.id,
        wallet_id=wallet.id,
        user_id=user.id
    )
    db.session.add(budget)
    db.session.commit()
    return budget

#################################################
# Tests
#################################################

class BudgetTests(TestCase):
    """Tests for budget functionality."""

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
        
        # Create test user, wallet, and category for budget tests
        self.test_user = create_test_user()
        self.test_wallet = create_test_wallet(self.test_user)
        self.test_category = create_test_category(self.test_user)
        
        # Login the test user
        with self.client as c:
            c.post('/login', data={
                'email': 'budget_test@example.com',
                'password': 'password',
                'submit': 'Log In'
            }, follow_redirects=True)

    def tearDown(self):
        """Executed after each test."""
        # Remove database session
        db.session.remove()
        
        # Drop all tables
        db.drop_all()
        
        # Pop the application context
        self.app_context.pop()

    def test_create_budget(self):
        """Test budget creation functionality."""
        post_data = {
            'amount': 300.00,
            'month': 'FEB',
            'year': 2025,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id
        }
        
        # Make request to the budget create route
        response = self.client.post('/budget/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check that the budget now exists in the database
        budget = Budget.query.filter_by(
            user_id=self.test_user.id,
            month=MonthList.FEB
        ).first()
        
        self.assertIsNotNone(budget)
        self.assertEqual(float(budget.amount), 300.00)
        self.assertEqual(budget.month, MonthList.FEB)
        self.assertEqual(budget.year, 2025)
        self.assertEqual(budget.category_id, self.test_category.id)
        self.assertEqual(budget.wallet_id, self.test_wallet.id)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('New budget was created successfully', response_text)

    def test_duplicate_budget(self):
        """Test creating a duplicate budget for same category, wallet, month, and year."""
        # Create an initial budget
        existing_budget = Budget.query.filter_by(
            user_id=self.test_user.id,
            month=MonthList.JAN,
            year=2025,
            category_id=self.test_category.id,
            wallet_id=self.test_wallet.id
        ).first()
        
        if not existing_budget:
            budget = create_test_budget(self.test_user, self.test_wallet, self.test_category)
        else:
            budget = existing_budget
        
        # Try to create the same budget again
        post_data = {
            'amount': 300.00,
            'month': 'JAN',
            'year': 2025,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id
        }
        
        # Make request to the budget create route
        response = self.client.post('/budget/create', data=post_data, follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check error message
        response_text = response.get_data(as_text=True)
        self.assertIn('You already have a budget for this category and period in wallet', response_text)
        
        # Verify only one budget exists
        budgets_count = Budget.query.filter_by(
            user_id=self.test_user.id,
            month=MonthList.JAN,
            year=2025,
            category_id=self.test_category.id,
            wallet_id=self.test_wallet.id
        ).count()
        
        self.assertEqual(budgets_count, 1)

    def test_update_budget(self):
        """Test budget update functionality."""
        # Create a budget to update or use existing one
        budget = Budget.query.filter_by(
            user_id=self.test_user.id,
            month=MonthList.JAN,
            year=2025,
            category_id=self.test_category.id,
            wallet_id=self.test_wallet.id
        ).first()
        
        if not budget:
            budget = create_test_budget(self.test_user, self.test_wallet, self.test_category)
        
        # Update data
        update_data = {
            'amount': 750.00,
            'month': 'MAR',
            'year': 2025,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id
        }
        
        # Make request to update the budget
        response = self.client.post(f'/budget/{budget.id}/update', 
                                    data=update_data, 
                                    follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Verify the budget was updated
        updated_budget = db.session.get(Budget, budget.id)
        self.assertEqual(float(updated_budget.amount), 750.00)
        self.assertEqual(updated_budget.month, MonthList.MAR)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Budget updated successfully', response_text)

    def test_delete_budget(self):
        """Test budget deletion functionality."""
        # Create a budget to delete or use existing one
        budget = Budget.query.filter_by(
            user_id=self.test_user.id,
            month=MonthList.JAN,
            year=2025,
            category_id=self.test_category.id,
            wallet_id=self.test_wallet.id
        ).first()
        
        if not budget:
            budget = create_test_budget(self.test_user, self.test_wallet, self.test_category)
        
        budget_id = budget.id
        
        # Make request to delete the budget
        response = self.client.post(f'/budget/{budget_id}/delete', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Verify the budget was deleted
        deleted_budget = db.session.get(Budget, budget_id)
        self.assertIsNone(deleted_budget)
        
        # Check success message
        response_text = response.get_data(as_text=True)
        self.assertIn('Budget deleted successfully', response_text)

    def test_access_other_user_budget(self):
        """Test accessing another user's budget."""
        # Create another user with a budget
        # Check if the other user already exists
        other_email = 'other@example.com'
        other_user = User.query.filter_by(email=other_email).first()
        
        if not other_user:
            other_user = User(
                first_name='Other',
                last_name='User',
                email=other_email,
                password=bcrypt.generate_password_hash('password').decode('utf-8')
            )
            db.session.add(other_user)
            db.session.commit()
        
        other_category = create_test_category(other_user)
        other_wallet = create_test_wallet(other_user)
        
        # Create a new budget or use an existing one
        other_budget = Budget.query.filter_by(
            user_id=other_user.id,
            month=MonthList.JAN,
            year=2025,
            category_id=other_category.id,
            wallet_id=other_wallet.id
        ).first()
        
        if not other_budget:
            other_budget = create_test_budget(other_user, other_wallet, other_category)
        
        # Try to access the other user's budget
        response = self.client.get(f'/budget/{other_budget.id}', follow_redirects=True)
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Check access denied message
        response_text = response.get_data(as_text=True)
        self.assertIn('Budget not found or access denied', response_text)
        
        # Try to update the other user's budget
        update_data = {
            'amount': 100.00,
            'month': 'APR',
            'year': 2025,
            'category_id': self.test_category.id,
            'wallet_id': self.test_wallet.id
        }
        
        response = self.client.post(f'/budget/{other_budget.id}/update', 
                                    data=update_data,
                                    follow_redirects=True)
        
        # Check that the budget was not updated and access denied
        self.assertIn('Budget not found or access denied', response.get_data(as_text=True))
        
        # Try to delete the other user's budget
        response = self.client.post(f'/budget/{other_budget.id}/delete', follow_redirects=True)
        
        # Check that the budget was not deleted and access denied
        self.assertIn('Budget not found or access denied', response.get_data(as_text=True))
        
        # Verify the budget still exists
        other_budget = db.session.get(Budget, other_budget.id)
        self.assertIsNotNone(other_budget)
