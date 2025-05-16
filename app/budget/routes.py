# app/budget/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Budget
from app.budget.forms import BudgetForm
from app.extensions import db
from app.enum import MonthList

budget = Blueprint('budget', __name__)

@budget.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  form = BudgetForm()
  
  # Populate the category and wallet dropdowns with current user's data
  categories = current_user.categories.all()
  wallets = current_user.wallets.filter_by(is_active=True).all()
  
  # Check if user has categories and wallets
  if not categories:
    flash("You need to create at least one category first")
    return redirect(url_for('category.create'))
  
  if not wallets:
    flash("You need to create at least one wallet first")
    return redirect(url_for('wallet.create'))
  
  form.category_id.choices = [(c.id, c.name) for c in categories]
  form.wallet_id.choices = [(w.id, w.name) for w in wallets]
  
  if form.validate_on_submit():
    # Check if budget category already exist in the wallet
    existing_budget = Budget.query.filter_by(
      user_id=current_user.id,
      category_id=form.category_id.data,
      month=form.month.data,
      year=form.year.data,
      wallet_id=form.wallet_id.data 
    ).first()
    
    # If it exist, do this:
    if existing_budget:
      flash("You already have a budget for this category and period in wallet")
      return render_template('create_budget.html', form=form)
    
    # Create new budget
    new_budget = Budget(
      amount=form.amount.data,
      month=form.month.data,
      year=form.year.data,
      category_id=form.category_id.data,
      wallet_id=form.wallet_id.data,
      user_id=current_user.id
    )
    
    db.session.add(new_budget)
    db.session.commit()
    
    flash('New budget was created successfully')
    return redirect(url_for('budget.detail', budget_id=new_budget.id))
  return render_template('create_budget.html', form=form)

@budget.route('/<int:budget_id>')
@login_required
def detail(budget_id):
  budget = db.session.get(Budget, budget_id)
  
  # Check if budget exists and belongs to current user
  if not budget or budget.user_id != current_user.id:
    flash('Budget not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Get all related data
  wallet = budget.wallet
  category = budget.category
  
  return render_template('budget_detail.html',
        budget=budget,
        wallet=wallet,
        category=category)


@budget.route('/<int:budget_id>/update', methods=['GET', 'POST'])
@login_required
def update(budget_id):
  budget = db.session.get(Budget, budget_id)
  
  # Check if budget exists and belongs to the current user
  if not budget or budget.user_id != current_user.id:
    flash('Budget not found or access denied')
    return redirect(url_for('main.dashboard'))

  form = BudgetForm()

  # Populate the category and wallet dropdowns with current user's data
  form.category_id.choices = [(c.id, c.name) for c in current_user.categories.all()]
  form.wallet_id.choices = [(w.id, w.name) for w in current_user.wallets.filter_by(is_active=True).all()]

  if request.method == 'POST':
    if form.validate_on_submit():
      budget.amount = form.amount.data
      budget.month = MonthList[form.month.data]
      budget.year = int(form.year.data)
      budget.category_id = form.category_id.data
      budget.wallet_id = form.wallet_id.data
      
      db.session.commit()
      
      flash('Budget updated successfully')
      return redirect(url_for('budget.detail', budget_id=budget_id))
  else:
    # Populate form with existing data
    form.amount.data = budget.amount
    form.month.data = budget.month.name
    form.year.data = str(budget.year)
    form.category_id.data = budget.category_id
    form.wallet_id.data = budget.wallet_id
  
  return render_template('update_budget.html', budget=budget, form=form)


@budget.route('/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete(budget_id):
  budget = db.session.get(Budget, budget_id)
  
  # Check if budget exists and belongs to the current user
  if not budget or budget.user_id != current_user.id:
    flash('Budget not found or access denied')
    return redirect(url_for('main.dashboard'))

  db.session.delete(budget)
  db.session.commit()
  flash('Budget deleted successfully')
  return redirect(url_for('main.dashboard'))
