from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Wallet, Budget, Transaction, Category, Label

from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def homepage():
  """Homepage"""
  if current_user.is_authenticated:
    return redirect(url_for('main.dashboard'))
  return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
  """Dashboard shows only current user's data"""
  user_wallets = current_user.wallets.filter_by(is_active=True).all()
  user_budgets = current_user.budgets.all()
  user_transactions = current_user.transactions.order_by(Transaction.date.desc()).limit(10).all()
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

##########################################################################
####          BUDGET             ####
##########################################################################



##########################################################################
####          LABEL           ####
##########################################################################

@main.route('/create_label', method=['GET', 'POST'])
@login_required
def create_label():
  form = LabelForm()
  
  if form.validate_on_submit():
    new_label = Label(
      name=form.name.data
    )
    
    db.session.add(new_label)
    db.session.commit()
    
    flash('New label created successfully')
    return redirect(url_for('main.label_detail', label_id=new_label.id))
  return render_template('create_label.html', form=form)


##########################################################################
####          TRANSACTION           ####
##########################################################################

@main.route('/create_transaction', method=['GET', 'POST'])
@login_required
def create_transaction():
  form = TransactionForm()
  
  if form.validate_on_submit():
    new_transaction = Transaction(
      amount=form.amount.data,
      description=form.description.data,
      date=form.date.data,
      is_expense=form.is_expense.data,
      # TODO: category_id
      # TODO: wallet_id
      # TODO: labels
    )
    
    db.session.add(new_transaction)
    db.session.commit()
    
    flash('New Transaction created successfully')
    return redirect(url_for('main.transaction_detail.html', transaction_id=new_transaction.id))
  return render_template('create_transaction.html', form=form)


##########################################################################
####          CATEGORY           ####
##########################################################################
@main.route('/create_category', method=['GET', 'POST'])
@login_required
def create_category():
  form = CategoryForm
  
  if form.validate_on_submit():
    new_category = Category(
      name=form.name.data,
      color=form.color.data,
      icon=form.icon.data
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    flash('New category created successfully')
    return redirect(url_for('main.category_detail', category_id=new_category.id))
  return render_template('create_category.html', form=form)
