from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Wallet, Transaction, Budget
from app.main import main

@main.route('/')
def homepage():
    """Homepage"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Dashboard shows only current user's data"""
    user_wallets = current_user.wallets.filter_by(is_active=True).all()
    user_budgets = current_user.budgets.all()
    user_transactions = current_user.transactions.order_by(
        Transaction.date.desc()).limit(10).all()
    user_labels = current_user.labels.all()
    user_categories = current_user.categories.all()
    
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
