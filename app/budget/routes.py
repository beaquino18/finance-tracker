# app/budget/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Budget, Transaction
from app.budget.forms import BudgetForm
from app.extensions import db
from app.enum import MonthList
from sqlalchemy import extract
from datetime import datetime
from collections import defaultdict

budget = Blueprint('budget', __name__, url_prefix='/budget')

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
  
  # Get wallet_id from request args if it exists
  wallet_id = request.args.get('wallet_id')
  
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
    return redirect(url_for('budget.overview'))
  return render_template('create_budget.html', form=form, wallet_id=wallet_id)

@budget.route('/overview')
@login_required
def overview():
    """Budget overview page with visual progress bars"""
    # Get filter parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    wallet_id = request.args.get('wallet_id', type=int)
    
    # Default to current month/year if not specified
    if not month or not year:
        now = datetime.now()
        month = now.month
        year = now.year
    
    # Build query
    query = Budget.query.filter_by(user_id=current_user.id)
    
    if wallet_id:
        query = query.filter_by(wallet_id=wallet_id)
    
    # Convert month number to MonthList enum using MONTH_MAPPING
    from app.seed_data import MONTH_MAPPING
    month_enum = MONTH_MAPPING.get(month)
    
    if month_enum:
        query = query.filter_by(month=month_enum, year=year)
    
    budgets = query.all()
    
    # Calculate spending for each budget
    budget_data = []
    for budget in budgets:
        # Get month number from enum using reverse lookup in MONTH_MAPPING
        budget_month = None
        for month_num, month_enum in MONTH_MAPPING.items():
            if month_enum == budget.month:
                budget_month = month_num
                break
        
        if not budget_month:
            continue
        
        # Query transactions for this budget's category, month, and year
        spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == budget.category_id,
            Transaction.wallet_id == budget.wallet_id,
            Transaction.is_expense == True,
            extract('month', Transaction.date) == budget_month,
            extract('year', Transaction.date) == budget.year
        ).scalar() or 0
        
        spent = float(spent)
        budget_amount = float(budget.amount)
        
        # Calculate percentage
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        
        # Determine color based on percentage
        if percentage >= 100:
            color = '#dc2626'  # Red
            status = 'over'
        elif percentage >= 80:
            color = '#f59e0b'  # Yellow/Amber
            status = 'warning'
        else:
            color = '#10b981'  # Green
            status = 'good'
        
        remaining = budget_amount - spent
        
        # Get last day of month
        from calendar import monthrange
        # Get the month number from the enum (1-12)
        budget_month_num = list(MonthList).index(budget.month) if budget.month in MonthList else 1
        last_day = monthrange(budget.year, budget_month_num)[1]
        
        budget_data.append({
            'id': budget.id,
            'category': budget.category,
            'wallet': budget.wallet,
            'amount': budget_amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': round(percentage, 1),
            'color': color,
            'status': status,
            'month': budget.month.value,
            'year': budget.year,
            'month_start': 1,
            'month_end': last_day
        })
    
    # Get all wallets for filter
    wallets = current_user.wallets.filter_by(is_active=True).all()
    
    # Generate month/year options
    current_year = datetime.now().year
    years = list(range(current_year - 2, current_year + 3))
    months = [
        {'num': i+1, 'name': m.value} 
        for i, m in enumerate(MonthList) 
        if m != MonthList.BLANK
    ]
    
    return render_template('budget_overview.html',
                         budgets=budget_data,
                         wallets=wallets,
                         months=months,
                         years=years,
                         selected_month=month,
                         selected_year=year,
                         selected_wallet_id=wallet_id)

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

  # Get wallet_id from request args if it exists
  wallet_id = request.args.get('wallet_id')
  
  if request.method == 'POST':
    if form.validate_on_submit():
      budget.amount = form.amount.data
      budget.month = form.month.data
      budget.year = int(form.year.data)
      budget.category_id = form.category_id.data
      budget.wallet_id = form.wallet_id.data
      
      db.session.commit()
      
      flash('Budget updated successfully')
      return redirect(url_for('budget.overview'))
  else:
    # Populate form with existing data
    form.amount.data = budget.amount
    form.month.data = budget.month.name
    form.year.data = str(budget.year)
    form.category_id.data = budget.category_id
    form.wallet_id.data = budget.wallet_id
  
  return render_template('update_budget.html', budget=budget, form=form, wallet_id=budget.wallet_id)


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
  return redirect(url_for('budget.overview'))
