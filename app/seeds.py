# app/seeds.py
"""Functions to seed the database with sample data."""
import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from app.extensions import db, bcrypt
from app.models import User, Wallet, Category, Label, Budget, Transaction, transaction_labels
from app.seed_data import (
    USERS, WALLETS, CATEGORIES, LABELS, 
    BUDGET_AMOUNTS, TRANSACTION_AMOUNTS, 
    TRANSACTION_DESCRIPTIONS, MONTH_MAPPING
)

def create_sample_users():
    """Create sample users using SQLAlchemy."""
    # Prepare user data with hashed passwords
    users_data = []
    for user in USERS:
        user_data = user.copy()
        user_data['password'] = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        users_data.append(user_data)
    
    # Check for existing users to avoid duplicates
    existing_emails = {user.email for user in User.query.all()}
    new_users_data = [data for data in users_data if data['email'] not in existing_emails]
    
    # Create users
    if new_users_data:
        try:
            # Bulk insert new users
            db.session.bulk_insert_mappings(User, new_users_data)
            db.session.commit()
            print(f"Created {len(new_users_data)} new users")
        except IntegrityError:
            db.session.rollback()
            print("Error creating users: IntegrityError")
    
    # Return all users (new and existing)
    return User.query.all()

def create_sample_wallets(users):
    """Create sample wallets for each user using SQLAlchemy."""
    wallets_data = []
    
    # Prepare data for bulk insert
    for user in users:
        # Get existing wallet names for this user
        existing_wallets = {wallet.name for wallet in Wallet.query.filter_by(user_id=user.id).all()}
        
        for template in WALLETS:
            if template['name'] not in existing_wallets:
                wallet_data = template.copy()
                wallet_data['user_id'] = user.id
                wallets_data.append(wallet_data)
    
    # Bulk insert new wallets
    if wallets_data:
        try:
            db.session.bulk_insert_mappings(Wallet, wallets_data)
            db.session.commit()
            print(f"Created {len(wallets_data)} new wallets")
        except IntegrityError:
            db.session.rollback()
            print("Error creating wallets: IntegrityError")
    
    # Return all wallets
    return Wallet.query.all()

def create_sample_categories(users):
    """Create sample categories for each user using SQLAlchemy."""
    categories_data = []
    
    # Prepare data for bulk insert
    for user in users:
        # Get existing category names for this user
        existing_categories = {category.name for category in Category.query.filter_by(user_id=user.id).all()}
        
        for template in CATEGORIES:
            if template['name'] not in existing_categories:
                category_data = template.copy()
                category_data['user_id'] = user.id
                categories_data.append(category_data)
    
    # Bulk insert new categories
    if categories_data:
        try:
            db.session.bulk_insert_mappings(Category, categories_data)
            db.session.commit()
            print(f"Created {len(categories_data)} new categories")
        except IntegrityError:
            db.session.rollback()
            print("Error creating categories: IntegrityError")
    
    # Return all categories
    return Category.query.all()

def create_sample_labels(users):
    """Create sample labels for each user using SQLAlchemy."""
    labels_data = []
    
    # Prepare data for bulk insert
    for user in users:
        # Get existing label names for this user
        existing_labels = {label.name for label in Label.query.filter_by(user_id=user.id).all()}
        
        for template in LABELS:
            if template['name'] not in existing_labels:
                label_data = template.copy()
                label_data['user_id'] = user.id
                labels_data.append(label_data)
    
    # Bulk insert new labels
    if labels_data:
        try:
            db.session.bulk_insert_mappings(Label, labels_data)
            db.session.commit()
            print(f"Created {len(labels_data)} new labels")
        except IntegrityError:
            db.session.rollback()
            print("Error creating labels: IntegrityError")
    
    # Return all labels
    return Label.query.all()

def create_sample_budgets(users, categories, wallets):
    """Create sample budgets for each user using SQLAlchemy."""
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    budgets_data = []
    
    # Check existing budgets to avoid duplicates
    existing_budgets = []
    for budget in Budget.query.filter_by(month=MONTH_MAPPING[current_month], year=current_year).all():
        existing_budgets.append((budget.user_id, budget.category_id, budget.wallet_id))
    
    # Prepare budget data for each user
    for user in users:
        user_categories = [cat for cat in categories if cat.user_id == user.id]
        user_wallets = [wallet for wallet in wallets if wallet.user_id == user.id]
        
        if not user_categories or not user_wallets:
            continue
        
        # Randomly select a wallet for all budgets
        wallet = random.choice(user_wallets)
        
        for category in user_categories:
            # Skip income category for budgeting
            if category.name == 'Income':
                continue
                
            # Skip if budget already exists
            if (user.id, category.id, wallet.id) in existing_budgets:
                continue
                
            # Generate budget amount based on category
            amount_range = BUDGET_AMOUNTS.get(category.name, BUDGET_AMOUNTS['Default'])
            amount = round(random.uniform(*amount_range), 2)
            
            # Add to bulk insert data
            budgets_data.append({
                'amount': amount,
                'month': MONTH_MAPPING[current_month],
                'year': current_year,
                'category_id': category.id,
                'wallet_id': wallet.id,
                'user_id': user.id
            })
    
    # Bulk insert budgets
    if budgets_data:
        try:
            db.session.bulk_insert_mappings(Budget, budgets_data)
            db.session.commit()
            print(f"Created {len(budgets_data)} new budgets")
        except IntegrityError:
            db.session.rollback()
            print("Error creating budgets: IntegrityError")
    
    # Return all budgets
    return Budget.query.all()

def create_sample_transactions(users, categories, wallets, labels):
    """Create sample transactions and transaction labels using SQLAlchemy."""
    # Generate date range for transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    transactions_data = []
    
    # Process each user
    for user in users:
        user_categories = [cat for cat in categories if cat.user_id == user.id]
        user_wallets = [wallet for wallet in wallets if wallet.user_id == user.id]
        
        if not user_categories or not user_wallets:
            continue
            
        # Generate 20-30 transactions per user
        num_transactions = random.randint(20, 30)
        
        for i in range(num_transactions):
            # Random date within range
            transaction_date = start_date + timedelta(days=random.randint(0, 30))
            
            # Randomly select category and wallet
            category = random.choice(user_categories)
            wallet = random.choice(user_wallets)
            
            # Determine if expense or income
            is_expense = category.name != 'Income'
            
            # Generate amount based on category
            amount_range = TRANSACTION_AMOUNTS.get(category.name, TRANSACTION_AMOUNTS['Default'])
            amount = round(random.uniform(*amount_range), 2)
            
            # Generate description
            description_list = TRANSACTION_DESCRIPTIONS.get(category.name, TRANSACTION_DESCRIPTIONS['Default'])
            description = random.choice(description_list)
            
            # Add transaction to bulk data
            transaction_data = {
                'amount': amount,
                'description': description,
                'date': transaction_date.date(),
                'is_expense': is_expense,
                'category_id': category.id,
                'wallet_id': wallet.id,
                'user_id': user.id
            }
            
            # Add to transactions data
            transactions_data.append(transaction_data)
    
    # Bulk insert transactions
    if transactions_data:
        try:
            db.session.bulk_insert_mappings(Transaction, transactions_data)
            db.session.commit()
            print(f"Created {len(transactions_data)} new transactions")
        except IntegrityError:
            db.session.rollback()
            print("Error creating transactions: IntegrityError")
            return []
    
    # Now assign labels to transactions (need transaction IDs, so we do this after commit)
    transactions = Transaction.query.filter(
        Transaction.date >= start_date.date(),
        Transaction.date <= end_date.date()
    ).all()
    
    # For each transaction, randomly assign 0-2 labels
    for transaction in transactions:
        user_labels = [label for label in labels if label.user_id == transaction.user_id]
        
        if user_labels:
            num_labels = random.randint(0, min(2, len(user_labels)))
            
            if num_labels > 0:
                selected_labels = random.sample(user_labels, num_labels)
                
                for label in selected_labels:
                    # Add to transaction_labels association table
                    db.session.execute(transaction_labels.insert().values(
                        transaction_id=transaction.id,
                        label_id=label.id
                    ))
    
    # Commit the label assignments
    try:
        db.session.commit()
        print("Assigned labels to transactions")
    except IntegrityError:
        db.session.rollback()
        print("Error assigning labels: IntegrityError")
    
    return transactions

def seed_database():
    """Main function to seed the database."""
    print("Starting database seeding...")
    
    # Create sample data
    users = create_sample_users()
    wallets = create_sample_wallets(users)
    categories = create_sample_categories(users)
    labels = create_sample_labels(users)
    budgets = create_sample_budgets(users, categories, wallets)
    transactions = create_sample_transactions(users, categories, wallets, labels)
    
    print("Database seeding completed successfully!")
