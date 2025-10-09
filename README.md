# Finance Tracker

![ERD - Budget Tracker](https://github.com/user-attachments/assets/3c9ed4c7-2837-4122-b318-c1150b639c23)

# FinFlow - Personal Finance Tracker

A comprehensive personal finance management application built with Flask, allowing users to track expenses, manage budgets, and monitor their financial health.

## Features

- **Wallet Management**: Create and manage multiple wallets (bank accounts, cash, credit cards)
- **Transaction Tracking**: Record income and expenses with detailed categorization
- **Budget Planning**: Set monthly budgets and track spending against targets
- **Categories & Labels**: Organize transactions with customizable categories and labels
- **Visual Analytics**: View spending patterns with interactive charts
- **Responsive Design**: Mobile-friendly interface with bottom navigation

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation Guide

### 1. Clone the Repository

```bash
git clone <repository-url>
cd finance-tracker
```

Or download and extract the ZIP file.

### 2. Create a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# .env
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
DATABASE_URL=sqlite:///instance/database.db
```

**To generate a secure secret key:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize the Database

The database will be automatically created when you first run the application. Optionally, you can seed it with sample data:

```bash
python seeds_runner.py
```

This will create:
- 2 sample users (Mickey Mouse and Minnie Mouse)
- Multiple wallets, categories, labels, budgets, and transactions for each user

**Default login credentials (after seeding):**
- Email: `mickey_mouse@gmail.com` or `minnie_mouse@gmail.com`
- Password: `password123`

### 6. Run the Application

**Development mode:**
```bash
python run.py
```

The application will be available at `http://localhost:5000`

**Production mode:**
```bash
gunicorn wsgi:app
```

## Project Structure

```
finance-tracker/
│
├── app/                          # Main application package
│   ├── auth/                     # Authentication blueprint
│   ├── budget/                   # Budget management
│   ├── category/                 # Category management
│   ├── label/                    # Label management
│   ├── main/                     # Main routes (dashboard, home)
│   ├── transaction/              # Transaction management
│   ├── wallet/                   # Wallet management
│   ├── static/                   # CSS, images, JavaScript
│   ├── templates/                # HTML templates
│   ├── models.py                 # Database models
│   ├── config.py                 # Configuration
│   └── __init__.py               # App factory
│
├── instance/                     # Instance folder (gitignored)
│   └── database.db              # SQLite database
│
├── .env                          # Environment variables (gitignored)
├── requirements.txt              # Python dependencies
├── run.py                        # Development server
└── README.md                     # This file
```

## Running Tests

Run the test suite:

```bash
# Run all tests
python -m unittest discover

# Run specific test modules
python -m unittest app.auth.tests
python -m unittest app.wallet.tests
python -m unittest app.budget.tests
python -m unittest app.transaction.tests
```

## Usage Guide

### First Time Setup

1. **Sign Up**: Create a new account at `/signup`
2. **Login**: Access your account at `/login`
3. **Create a Wallet**: Add your first wallet (e.g., "Bank Account", "Cash")
4. **Create Categories**: Set up expense categories (e.g., "Groceries", "Transportation")
5. **Add Transactions**: Start recording your income and expenses
6. **Set Budgets**: Create monthly budgets for your categories

### Key Features

- **Dashboard**: Overview of all wallets, recent transactions, categories, and labels
- **Transactions Page**: View cash flow chart and filter transactions by wallet, category, or label
- **Budget Overview**: Track spending against budgets with visual progress bars
- **Wallet Details**: View all transactions and budgets for a specific wallet

## Configuration

### Database

By default, the app uses SQLite. To use a different database, update `DATABASE_URL` in your `.env` file:

```bash
# PostgreSQL example
DATABASE_URL=postgresql://username:password@localhost/dbname

# MySQL example
DATABASE_URL=mysql://username:password@localhost/dbname
```

### Debug Mode

For production, ensure debug mode is disabled:

```bash
FLASK_DEBUG=False
```

## Deployment

### Heroku Deployment

1. Create a `Procfile` (already included):
```
web: gunicorn wsgi:app
```

2. Install Heroku CLI and deploy:
```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python seeds_runner.py  # Optional: seed database
```

### Other Platforms

The application can be deployed to any platform that supports Python/Flask:
- AWS Elastic Beanstalk
- Google Cloud Platform
- DigitalOcean
- Railway
- Render

## Troubleshooting

### Common Issues

**Database errors:**
```bash
# Reset the database
rm instance/database.db
python run.py
```

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Run on a different port
flask run --port 5001
```

## Security Notes

- Never commit `.env` file or `instance/` folder to version control
- Always use strong, unique passwords
- Use environment variables for sensitive configuration
- Enable HTTPS in production
- Regularly update dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the repository.

---

**Happy budgeting! 💰**
