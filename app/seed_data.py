# app/seed_data.py
"""Data definitions for database seeding."""
from app.enum import Color, MonthList, CategoryIcon

# User data
USERS = [
    {
        'first_name': 'Mickey',
        'last_name': 'Mouse',
        'email': 'mickey_mouse@gmail.com',
        'password': 'password123',
        'profile_image': '/static/images/default_avatar.png'
    },
    {
        'first_name': 'Minnie',
        'last_name': 'Mouse',
        'email': 'minnie_mouse@gmail.com',
        'password': 'password123',
        'profile_image': '/static/images/default_avatar.png'
    }
]

# Wallet templates
WALLETS = [
    {'name': 'Cash', 'balance': 500.00, 'color': Color.GREEN, 'is_active': True},
    {'name': 'Checking Account', 'balance': 2500.00, 'color': Color.NAVY, 'is_active': True},
    {'name': 'Savings Account', 'balance': 10000.00, 'color': Color.GOLD, 'is_active': True},
    {'name': 'Credit Card', 'balance': -450.00, 'color': Color.PURPLE, 'is_active': True}
]

# Category templates
CATEGORIES = [
    {'name': 'Groceries', 'color': Color.GREEN, 'icon': 'fa-shopping-cart'},
    {'name': 'Dining Out', 'color': Color.ORANGE_RED, 'icon': 'fa-utensils'},
    {'name': 'Transportation', 'color': Color.BLUE, 'icon': 'fa-car'},
    {'name': 'Housing', 'color': Color.NAVY, 'icon': 'fa-home'},
    {'name': 'Utilities', 'color': Color.RED, 'icon': 'fa-lightbulb'},
    {'name': 'Entertainment', 'color': Color.PURPLE, 'icon': 'fa-film'},
    {'name': 'Health', 'color': Color.EMERALD, 'icon': 'fa-heartbeat'},
    {'name': 'Income', 'color': Color.GOLD, 'icon': 'fa-dollar-sign'}
]

# Label templates
LABELS = [
    {'name': 'Essential'},
    {'name': 'Recurring'},
    {'name': 'Discretionary'},
    {'name': 'Work-related'},
    {'name': 'Tax-deductible'}
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
