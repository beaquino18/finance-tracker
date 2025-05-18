# app/main/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Wallet, Transaction, Budget, Category, Label

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Landing page for non-authenticated users."""
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
    return render_template('index.html')

@main.route('/home')
@login_required
def homepage():
    """Homepage for authenticated users - shows user info and wallets."""
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', wallets=wallets)

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
