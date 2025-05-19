# app/seeds.py
"""Database seeding script using direct model instances approach."""
import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.extensions import db
from app.models import User, Wallet, Category, Label, Budget, Transaction, transaction_labels
from app.seed_data import (
    USERS, WALLETS, CATEGORIES, LABELS,
    BUDGET_AMOUNTS, TRANSACTION_AMOUNTS, TRANSACTION_DESCRIPTIONS, MONTH_MAPPING
)

def seed_database():
    """Main function to seed the database with sample data."""
    print("Starting database seeding...")
    
    # Add base entities
    add_users()
    add_wallets()
    add_categories()
    add_labels()
    
    # Add transactions and budgets
    add_budgets()
    add_transactions()
    
    print("Database seeding completed successfully!")

def add_users():
    """Add sample users to the database."""
    # Create copies of the users to avoid modifying the originals
    users_to_add = []
    for user in USERS:
        # Creating a new user with the same attributes
        users_to_add.append(User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            profile_image=user.profile_image
        ))
    
    try:
        db.session.add_all(users_to_add)
        db.session.commit()
        print(f"Added {len(users_to_add)} users")
    except IntegrityError:
        db.session.rollback()
        print("Error adding users: IntegrityError (users might already exist)")

def add_wallets():
    """Add sample wallets for each user to the database."""
    users = User.query.all()
    wallets_to_add = []
    
    for user in users:
        for wallet_template in WALLETS:
            # Create a new wallet for each user based on the template
            wallet = Wallet(
                name=wallet_template.name,
                balance=wallet_template.balance,
                is_active=wallet_template.is_active,
                user_id=user.id
            )
            wallets_to_add.append(wallet)
    
    try:
        db.session.add_all(wallets_to_add)
        db.session.commit()
        print(f"Added {len(wallets_to_add)} wallets")
    except IntegrityError:
        db.session.rollback()
        print("Error adding wallets: IntegrityError")

def add_categories():
    """Add sample categories for each user to the database."""
    users = User.query.all()
    categories_to_add = []
    
    for user in users:
        for category_template in CATEGORIES:
            # Create a new category for each user based on the template
            category = Category(
                name=category_template.name,
                color=category_template.color,
                icon=category_template.icon,
                user_id=user.id
            )
            categories_to_add.append(category)
    
    try:
        db.session.add_all(categories_to_add)
        db.session.commit()
        print(f"Added {len(categories_to_add)} categories")
    except IntegrityError:
        db.session.rollback()
        print("Error adding categories: IntegrityError")

def add_labels():
    """Add sample labels for each user to the database."""
    users = User.query.all()
    labels_to_add = []
    
    for user in users:
        for label_template in LABELS:
            # Create a new label for each user based on the template
            label = Label(
                name=label_template.name,
                user_id=user.id
            )
            labels_to_add.append(label)
    
    try:
        db.session.add_all(labels_to_add)
        db.session.commit()
        print(f"Added {len(labels_to_add)} labels")
    except IntegrityError:
        db.session.rollback()
        print("Error adding labels: IntegrityError")

def add_budgets():
    """Add sample budgets for all users."""
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    users = User.query.all()
    budgets_to_add = []
    
    for user in users:
        # Get user's categories and wallets
        categories = Category.query.filter_by(user_id=user.id).all()
        wallets = Wallet.query.filter_by(user_id=user.id, is_active=True).all()
        
        if not categories or not wallets:
            continue
        
        # Randomly select a wallet for all budgets
        wallet = random.choice(wallets)
        
        for category in categories:
            # Skip income category for budgeting
            if category.name == 'Income':
                continue
            
            # Generate budget amount based on category
            amount_range = BUDGET_AMOUNTS.get(category.name, BUDGET_AMOUNTS['Default'])
            amount = round(random.uniform(*amount_range), 2)
            
            # Create budget
            budget = Budget(
                amount=amount,
                month=MONTH_MAPPING[current_month],
                year=current_year,
                category_id=category.id,
                wallet_id=wallet.id,
                user_id=user.id
            )
            budgets_to_add.append(budget)
    
    try:
        db.session.add_all(budgets_to_add)
        db.session.commit()
        print(f"Added {len(budgets_to_add)} budgets")
    except IntegrityError:
        db.session.rollback()
        print("Error adding budgets: IntegrityError")

def add_transactions():
    """Add sample transactions for all users."""
    # Generate date range for transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    users = User.query.all()
    transactions_to_add = []
    wallet_balance_updates = {}  # Track balance updates for each wallet
    transaction_label_pairs = []  # Track transaction and label IDs to connect
    
    for user in users:
        # Get user's categories, wallets, and labels
        categories = Category.query.filter_by(user_id=user.id).all()
        wallets = Wallet.query.filter_by(user_id=user.id, is_active=True).all()
        labels = Label.query.filter_by(user_id=user.id).all()
        
        if not categories or not wallets:
            continue
        
        # Generate 20-30 transactions per user
        num_transactions = random.randint(20, 30)
        
        for i in range(num_transactions):
            # Random date within range
            transaction_date = start_date + timedelta(days=random.randint(0, 30))
            
            # Randomly select category and wallet
            category = random.choice(categories)
            wallet = random.choice(wallets)
            
            # Determine if expense or income
            is_expense = category.name != 'Income'
            
            # Generate amount based on category
            amount_range = TRANSACTION_AMOUNTS.get(category.name, TRANSACTION_AMOUNTS['Default'])
            amount = round(random.uniform(*amount_range), 2)
            
            # Generate description
            description_list = TRANSACTION_DESCRIPTIONS.get(category.name, TRANSACTION_DESCRIPTIONS['Default'])
            description = random.choice(description_list)
            
            # Create transaction
            transaction = Transaction(
                amount=amount,
                description=description,
                date=transaction_date.date(),
                is_expense=is_expense,
                category_id=category.id,
                wallet_id=wallet.id,
                user_id=user.id
            )
            
            transactions_to_add.append(transaction)
            
            # Track balance updates for each wallet
            if wallet.id not in wallet_balance_updates:
                wallet_balance_updates[wallet.id] = 0
                
            # Update the balance tracking
            if is_expense:
                wallet_balance_updates[wallet.id] -= amount
            else:
                wallet_balance_updates[wallet.id] += amount
            
            # Prepare labels for this transaction (we'll add them after commit)
            if labels:
                num_labels = random.randint(0, min(2, len(labels)))
                if num_labels > 0:
                    selected_labels = random.sample(labels, num_labels)
                    # Store the transaction and its labels to add after commit
                    transaction_label_pairs.append((transaction, selected_labels))
    
    try:
        # First add all transactions
        db.session.add_all(transactions_to_add)
        db.session.commit()
        
        # Now that transactions are committed and have IDs, we can add labels
        label_associations_count = 0
        for transaction, labels_to_add in transaction_label_pairs:
            for label in labels_to_add:
                # Add the association directly using SQLAlchemy text
                sql = text("INSERT INTO transaction_labels (transaction_id, label_id) VALUES (:t_id, :l_id)")
                db.session.execute(sql, {"t_id": transaction.id, "l_id": label.id})
                label_associations_count += 1
        
        # Then update wallet balances
        for wallet_id, balance_change in wallet_balance_updates.items():
            wallet = Wallet.query.get(wallet_id)
            if wallet:
                # Use SQLAlchemy's update() for numeric operations
                current_balance = float(wallet.balance)
                new_balance = current_balance + balance_change
                wallet.balance = new_balance
        
        db.session.commit()
        print(f"Added {len(transactions_to_add)} transactions")
        print(f"Added {label_associations_count} transaction-label relationships")
        print(f"Updated balances for {len(wallet_balance_updates)} wallets")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error adding transactions: IntegrityError: {str(e)}")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding transactions: {str(e)}")



if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
