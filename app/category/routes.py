# app/category/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Category, Transaction, Budget
from app.category.forms import CategoryForm
from app.extensions import db
from app.enum import CategoryIcon, Color

category = Blueprint('category', __name__, url_prefix='/category')

@category.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CategoryForm(user=current_user)
    
    if form.validate_on_submit():
        # Convert string values to enum
        color_enum = Color[form.color.data]
        
        new_category = Category(
            name=form.name.data,
            color=color_enum,
            icon=form.icon.data,  # icon is already a string
            user_id=current_user.id
        )
        
        db.session.add(new_category)
        db.session.commit()
        
        flash('New category created successfully')
        return redirect(url_for('category.detail', category_id=new_category.id))
    
    return render_template('create_category.html', form=form)

@category.route('/<int:category_id>')
@login_required
def detail(category_id):
    category = db.session.get(Category, category_id)
    
    # Check if category exists and belongs to the current user
    if not category or category.user_id != current_user.id:
        flash('Category not found or access denied')
        return redirect(url_for('main.dashboard'))
    
    transactions = Transaction.query.filter_by(category_id=category.id).all()
    
    return render_template('category_detail.html', category=category, transactions=transactions)

@category.route('/<int:category_id>/update', methods=['GET', 'POST'])
@login_required
def update(category_id):
    category = db.session.get(Category, category_id)
    
    # Check if category exists and belongs to the current user
    if not category or category.user_id != current_user.id:
        flash('Category not found or access denied')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        form = CategoryForm(user=current_user, edit_category=category)
        
        # Process form submission (only for POST)
        if form.validate_on_submit():
            # Convert string values to enum
            color_enum = Color[form.color.data]
            
            category.name = form.name.data
            category.color = color_enum
            category.icon = form.icon.data  # icon is already a string
            
            db.session.commit()
            
            flash('Category updated successfully')
            return redirect(url_for('category.detail', category_id=category_id))
    else:
        # For GET requests, prepopulate the form
        form = CategoryForm(user=current_user, edit_category=category)
        # Set the current values in hidden fields (will be set by JavaScript)
        form.name.data = category.name
        form.color.data = category.color.name
        form.icon.data = category.icon
    
    return render_template('update_category.html', category=category, form=form)

@category.route('/<int:category_id>/delete', methods=['POST'])
@login_required
def delete(category_id):
    category = db.session.get(Category, category_id)
    
    # Check if category exists and belongs to the current user
    if not category or category.user_id != current_user.id:
        flash('Category not found or access denied')
        return redirect(url_for('main.dashboard'))
    
    # Check for related transactions or budgets before deletion
    transactions_count = Transaction.query.filter_by(category_id=category.id).count()
    budgets_count = Budget.query.filter_by(category_id=category.id).count()
    
    if transactions_count > 0 or budgets_count > 0:
        flash('Cannot delete category with existing transactions or budgets')
        return redirect(url_for('category.detail', category_id=category_id))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully')
    return redirect(url_for('main.dashboard'))
