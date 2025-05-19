# app/transaction/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Transaction, Wallet
from app.transaction.forms import TransactionForm
from app.extensions import db

transaction = Blueprint('transaction', __name__, url_prefix='/transaction')

@transaction.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  form = TransactionForm(user=current_user)
  
  if form.validate_on_submit():
    new_transaction = Transaction(
      amount=form.amount.data,
      description=form.description.data,
      date=form.date.data,
      is_expense=form.is_expense.data,
      category_id=form.category_id.data,
      wallet_id=form.wallet_id.data,
      user_id=current_user.id,
      labels=form.labels.data
    )
    
    # Update wallet balance based on transaction
    wallet = db.session.get(Wallet, form.wallet_id.data)
    if form.is_expense.data:
      wallet.balance -= form.amount.data
    else:
      wallet.balance += form.amount.data
    
    db.session.add(new_transaction)
    db.session.commit()
    
    flash('New Transaction created successfully')
    return redirect(url_for('transaction.detail', transaction_id=new_transaction.id))
  return render_template('create_transaction.html', form=form)

@transaction.route('/<int:transaction_id>')
@login_required
def detail(transaction_id):
  transaction = db.session.get(Transaction, transaction_id)

  # Check if transaction exists and belongs to the current user
  if not transaction or transaction.user_id != current_user.id:
    flash('Transaction not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  return render_template('transaction_detail.html', transaction=transaction)

@transaction.route('/<int:transaction_id>/update', methods=['GET', 'POST'])
@login_required
def update(transaction_id):
  transaction = db.session.get(Transaction, transaction_id)
  
  # Check if transaction exists and belongs to the current user
  if not transaction or transaction.user_id != current_user.id:
    flash('Transaction not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Store original values for wallet balance adjustment
  original_amount = transaction.amount
  original_is_expense = transaction.is_expense
  original_wallet_id = transaction.wallet_id
  
  if request.method == 'POST':
    form = TransactionForm(user=current_user)
    
    if form.validate_on_submit():
      # Update wallet balances
      if original_wallet_id == form.wallet_id.data:
        # Same wallet, just update the balance difference
        wallet = transaction.wallet
        # Undo original transaction effect
        if original_is_expense:
          wallet.balance += original_amount
        else:
          wallet.balance -= original_amount
        
        # Apply new transaction effect
        if form.is_expense.data:
          wallet.balance -= form.amount.data
        else:
          wallet.balance += form.amount.data
      else:
        # Different wallets, update both
        old_wallet = db.session.get(Wallet, original_wallet_id)
        new_wallet = db.session.get(Wallet, form.wallet_id.data)
        
        # Undo effect on old wallet
        if original_is_expense:
          old_wallet.balance += original_amount
        else:
          old_wallet.balance -= original_amount
          
        # Apply effect on new wallet
        if form.is_expense.data:
          new_wallet.balance -= form.amount.data
        else:
          new_wallet.balance += form.amount.data
      
      # Update transaction
      transaction.amount = form.amount.data
      transaction.description = form.description.data
      transaction.date = form.date.data
      transaction.is_expense = form.is_expense.data
      transaction.category_id = form.category_id.data
      transaction.wallet_id = form.wallet_id.data
      transaction.labels = form.labels.data
      
      db.session.commit()
      
      flash('Transaction updated successfully')
      return redirect(url_for('transaction.detail', transaction_id=transaction_id))
  else:
    form = TransactionForm(obj=transaction, user=current_user)
    
  return render_template('update_transaction.html', transaction=transaction, form=form)

@transaction.route('/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete(transaction_id):
  transaction = db.session.get(Transaction, transaction_id)
  
  # Check if transaction exists and belongs to the current user
  if not transaction or transaction.user_id != current_user.id:
    flash('Transaction not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Update wallet balance
  wallet = transaction.wallet
  if transaction.is_expense:
    wallet.balance += transaction.amount
  else:
    wallet.balance -= transaction.amount
  
  db.session.delete(transaction)
  db.session.commit()
  
  flash('Transaction deleted successfully')
  return redirect(url_for('wallet.detail', wallet_id=transaction.wallet_id))
