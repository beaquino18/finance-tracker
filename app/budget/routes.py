from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Budget
from app.main.forms import BudgetForm
from app.extensions import db

budget_bp = Blueprint('budget', __name__, url_prefix='/budget')

@budget_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  form = BudgetForm()
  
  # Populate the category and wallet dropdowns with current user's data
  form.category_id.choices = [(c.id, c.name) for c in current_user.categories.all()]
  form.wallet_id.choices = [(w.id, w.name) for w in current_user.wallets.filter_by(is_active=True).all()]
  
  if form.validate_on_submit():
    # Check if budget category already exist in the wallet
    existing_budget = Budget.query.filter_by(
      user=current_user.id,
      category_id=form.category_id.data,
      month=form.month.data,
      year=form.year.data,
      wallet_id=form.wallet_id.data 
    ).first()
    
    # If it exist, do this:
    if existing_budget:
      flash("You already have a budge for this category and period in wallet")
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
    
    flash('New wallet was created successfully')
    return redirect(url_for('main.budget_detail', budget_id=new_budget.id))
  return render_template('create_budget.html', form=form)
