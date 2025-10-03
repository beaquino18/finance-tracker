# app/main/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Wallet, Transaction, Budget, Category, Label
from sqlalchemy import extract
from datetime import datetime, timedelta
from collections import defaultdict

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Landing page for non-authenticated users."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard shows only current user's data"""
    user_wallets = Wallet.query.filter_by(user_id=current_user.id, is_active=True).all()
    user_budgets = Budget.query.filter_by(user_id=current_user.id).all()
    user_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.date.desc()).limit(5).all()
    user_labels = Label.query.filter_by(user_id=current_user.id).all()
    user_categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Summary Stats
    total_balance = sum(wallet.balance for wallet in user_wallets)
    active_wallets_count = len(user_wallets)
    
    return render_template('dashboard.html',
            user=current_user,
            wallets=user_wallets,
            recent_transactions=user_transactions,
            labels=user_labels,
            categories=user_categories,
            budgets=user_budgets,
            total_balance=total_balance,
            active_wallets_count=active_wallets_count)

@main.route('/transactions')
@login_required
def transactions():
    """Transactions page with cash flow chart and transaction list"""
    
    # Get filter parameters
    wallet_id = request.args.get('wallet_id', type=int)
    category_id = request.args.get('category_id', type=int)
    label_id = request.args.get('label_id', type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    # Month names for display
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    filter_display = None
    
    if month and year:
        filter_display = f"{month_names[month - 1]} {year}"
    
    # Base query for user's transactions
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if wallet_id:
        query = query.filter_by(wallet_id=wallet_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if label_id:
        query = query.filter(Transaction.labels.any(id=label_id))
    if month and year:
        query = query.filter(
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        )
    
    # Get all transactions for the list
    all_transactions = query.order_by(Transaction.date.desc()).all()
    
    # Calculate cash flow data for the last 6 months
    today = datetime.now()
    
    # Get transactions for cash flow chart (last 6 months)
    six_months_ago = today - timedelta(days=180)
    cash_flow_transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= six_months_ago.date()
    ).all()
    
    # Calculate monthly income and expenses with proper month ordering
    monthly_data = {}
    
    # Initialize data for each of the last 6 months
    for i in range(6):
        month_date = today - timedelta(days=30 * (5 - i))
        month_key = month_date.strftime('%b %Y')
        monthly_data[month_key] = {'income': 0, 'expense': 0}
    
    # Populate with actual transaction data
    for transaction in cash_flow_transactions:
        month_key = transaction.date.strftime('%b %Y')
        if month_key in monthly_data:
            if transaction.is_expense:
                monthly_data[month_key]['expense'] += float(transaction.amount)
            else:
                monthly_data[month_key]['income'] += float(transaction.amount)
    
    # Create ordered lists for the chart
    chart_months = list(monthly_data.keys())
    chart_income = [monthly_data[month]['income'] for month in chart_months]
    chart_expense = [monthly_data[month]['expense'] for month in chart_months]
    
    # Group transactions by date for display
    transactions_by_date = defaultdict(list)
    for transaction in all_transactions:
        date_key = transaction.date.strftime('%b %d, %Y')
        transactions_by_date[date_key].append(transaction)
    
    # Calculate total balance
    user_wallets = Wallet.query.filter_by(user_id=current_user.id, is_active=True).all()
    total_balance = sum(wallet.balance for wallet in user_wallets)
    
    # Get filter options
    all_wallets = Wallet.query.filter_by(user_id=current_user.id).all()
    all_categories = Category.query.filter_by(user_id=current_user.id).all()
    all_labels = Label.query.filter_by(user_id=current_user.id).all()
    
    return render_template('transactions.html',
                         transactions_by_date=transactions_by_date,
                         total_balance=total_balance,
                         chart_months=chart_months,
                         chart_income=chart_income,
                         chart_expense=chart_expense,
                         all_wallets=all_wallets,
                         all_categories=all_categories,
                         all_labels=all_labels,
                         current_wallet_id=wallet_id,
                         current_category_id=category_id,
                         current_label_id=label_id,
                         filter_display=filter_display)
