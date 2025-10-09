# app/wallet/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Wallet
from app.wallet.forms import WalletForm
from app.extensions import db

wallet = Blueprint('wallet', __name__, url_prefix='/wallet')

@wallet.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  form = WalletForm()
  
  if form.validate_on_submit():
    # Check if wallet with same name already exists for this user
    existing_wallet = Wallet.query.filter_by(
      name=form.name.data,
      user_id=current_user.id
    ).first()
    
    if existing_wallet:
      flash("You already have a wallet with this name")
      return render_template('create_wallet.html', form=form)
    
    new_wallet = Wallet(
      name=form.name.data,
      balance=form.balance.data,
      is_active=form.is_active.data,
      user_id=current_user.id
    )
    db.session.add(new_wallet)
    db.session.commit()
    
    flash('New Wallet was created successfully')
    return redirect(url_for('wallet.detail', wallet_id=new_wallet.id))
  return render_template('create_wallet.html', form=form)

@wallet.route('/<int:wallet_id>')
@login_required
def detail(wallet_id):
  wallet = db.session.get(Wallet, wallet_id)
  
  # Check if wallet exists and belongs to current user
  if not wallet or wallet.user_id != current_user.id:
    flash('Wallet not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Get all related data
  budgets = wallet.budgets.all()
  transactions = wallet.transactions.all()
  
  return render_template('wallet_detail.html',
            wallet=wallet,
            budgets=budgets,
            transactions=transactions)
  

@wallet.route('/<int:wallet_id>/update', methods=['GET', 'POST'])
@login_required
def update(wallet_id):
    wallet = db.session.get(Wallet, wallet_id)
    
    # Check if wallet exists and belongs to current user
    if not wallet or wallet.user_id != current_user.id:
        flash('Wallet not found or access denied')
        return redirect(url_for('main.dashboard'))
    
    # Create form - for GET requests, prepopulate with wallet data
    form = WalletForm(obj=wallet)
    
    if request.method == 'POST':
        form = WalletForm()
        if form.validate_on_submit():
            wallet.name = form.name.data
            wallet.balance = form.balance.data
            wallet.is_active = form.is_active.data
            
            db.session.commit()
            
            flash('Wallet updated successfully')
            return redirect(url_for('wallet.detail', wallet_id=wallet_id))
            
    return render_template('update_wallet.html', wallet=wallet, form=form)

@wallet.route('/<int:wallet_id>/delete', methods=['POST'])
@login_required
def delete(wallet_id):
  wallet = db.session.get(Wallet, wallet_id)
  
  # Check if wallet exists and belongs to current user
  if not wallet or wallet.user_id != current_user.id:
    flash('Wallet not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Check if wallet has transactions or budgets
  if wallet.transactions.count() > 0 or wallet.budgets.count() > 0:
    flash('Cannot delete wallet with existing transactions or budgets')
    return redirect(url_for('wallet.detail', wallet_id=wallet_id))
  
  db.session.delete(wallet)
  db.session.commit()
  flash('Wallet deleted successfully')
  return redirect(url_for('main.dashboard'))
