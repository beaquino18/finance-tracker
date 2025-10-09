# app/seed_data.py
"""Data definitions for database seeding using direct model instances."""
from app.extensions import bcrypt
from app.models import User, Wallet, Category, Label, Budget, Transaction
from app.enum import Color, MonthList, CategoryIcon

# User instances
USERS = [
    User(
        first_name='Mickey',
        last_name='Mouse',
        email='mickey_mouse@gmail.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        profile_image='/static/images/default_avatar.png'
    ),
    User(
        first_name='Minnie',
        last_name='Mouse',
        email='minnie_mouse@gmail.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        profile_image='/static/images/default_avatar.png'
    )
]

# Wallet templates
WALLETS = [
    # Will be created for each user
    Wallet(name='Cash', balance=500.00, is_active=True),
    Wallet(name='Checking Account', balance=2500.00, is_active=True),
    Wallet(name='Savings Account', balance=10000.00, is_active=True),
    Wallet(name='Credit Card', balance=-450.00, is_active=True)
]

# Category templates
CATEGORIES = [
    # Will be created for each user
    Category(name='Groceries', color=Color.GREEN, icon='fa-shopping-cart'),
    Category(name='Dining Out', color=Color.ORANGE_RED, icon='fa-utensils'),
    Category(name='Transportation', color=Color.BLUE, icon='fa-car'),
    Category(name='Housing', color=Color.NAVY, icon='fa-home'),
    Category(name='Utilities', color=Color.RED, icon='fa-lightbulb'),
    Category(name='Entertainment', color=Color.PURPLE, icon='fa-film'),
    Category(name='Health', color=Color.EMERALD, icon='fa-heartbeat'),
    Category(name='Income', color=Color.GOLD, icon='fa-dollar-sign')
]

# Label templates
LABELS = [
    # Will be created for each user
    Label(name='Essential'),
    Label(name='Recurring'),
    Label(name='Discretionary'),
    Label(name='Work-related'),
    Label(name='Tax-deductible')
]

# Budget amount ranges by category
BUDGET_AMOUNTS = {
    'Housing': (800, 1500),
    'Groceries': (300, 600),
    'Dining Out': (100, 300),
    'Transportation': (150, 400),
    'Utilities': (100, 300),
    'Entertainment': (50, 200),
    'Health': (100, 400),
    'Default': (50, 200)  # Default range for other categories
}

# Transaction amounts by category
TRANSACTION_AMOUNTS = {
    'Income': (1000, 3000),
    'Housing': (800, 1500),
    'Groceries': (20, 150),
    'Dining Out': (15, 100),
    'Transportation': (5, 80),
    'Utilities': (50, 200),
    'Entertainment': (10, 100),
    'Health': (20, 200),
    'Default': (10, 100)  # Default range for other categories
}

# Transaction descriptions by category
TRANSACTION_DESCRIPTIONS = {
    'Groceries': ['Supermarket', 'Grocery Store', 'Local Market', 'Whole Foods', 'Trader Joe\'s'],
    'Dining Out': ['Restaurant', 'Cafe', 'Fast Food', 'Coffee Shop', 'Lunch'],
    'Transportation': ['Gas Station', 'Public Transit', 'Uber', 'Lyft', 'Parking'],
    'Housing': ['Rent', 'Mortgage', 'Home Insurance', 'Property Tax', 'HOA Fees'],
    'Utilities': ['Electricity Bill', 'Water Bill', 'Internet', 'Phone Bill', 'Gas Bill'],
    'Entertainment': ['Movie Theater', 'Concert', 'Streaming Service', 'Video Games', 'Subscription'],
    'Health': ['Pharmacy', 'Doctor Visit', 'Health Insurance', 'Gym Membership', 'Vitamins'],
    'Income': ['Salary', 'Freelance Payment', 'Dividend', 'Side Gig', 'Refund'],
    'Default': ['Miscellaneous', 'Purchase', 'Payment', 'Service', 'Fee']
}

# Month mapping
MONTH_MAPPING = {
    1: MonthList.JAN,
    2: MonthList.FEB,
    3: MonthList.MAR,
    4: MonthList.APR,
    5: MonthList.MAY,
    6: MonthList.JUN,
    7: MonthList.JUL,
    8: MonthList.AUG,
    9: MonthList.SEP,
    10: MonthList.OCT,
    11: MonthList.NOV,
    12: MonthList.DEC
}
