# app/label/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Label
from app.label.forms import LabelForm
from app.extensions import db

label = Blueprint('label', __name__)

@label.route('/create', methods=['GET', 'POST'])
@login_required
def create():
  form = LabelForm(user=current_user)
  
  if form.validate_on_submit():
    new_label = Label(
      name=form.name.data,
      user_id=current_user.id
    )
    
    db.session.add(new_label)
    db.session.commit()
    
    flash('New label created successfully')
    return redirect(url_for('label.detail', label_id=new_label.id))
  return render_template('create_label.html', form=form)

@label.route('/<int:label_id>')
@login_required
def detail(label_id):
  label = db.session.get(Label, label_id)
  
  # Check if label exists and belongs to the current user
  if not label or label.user_id != current_user.id:
    flash('Label not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Get transactions using the many-to-many relationship
  transactions = label.transactions.all()
  
  return render_template('label_detail.html', label=label, transactions=transactions)

@label.route('/<int:label_id>/update', methods=['GET', 'POST'])
@login_required
def update(label_id):
  label = db.session.get(Label, label_id)
  
  # Check if label exists and belongs to the current user
  if not label or label.user_id != current_user.id:
    flash('Label not found or access denied')
    return redirect(url_for('main.dashboard'))

  # Create the form - use obj=label for GET to prepopulate
  if request.method == 'POST':
    form = LabelForm(user=current_user, edit_label=label)
    
    # Process form submission (only for POST)
    if form.validate_on_submit():
      label.name = form.name.data
      
      db.session.commit()
      
      flash('Label updated successfully')
      return redirect(url_for('label.detail', label_id=label_id))
  else:
    form = LabelForm(obj=label, user=current_user, edit_label=label)
  
  return render_template('update_label.html', label=label, form=form)

@label.route('/<int:label_id>/delete', methods=['POST'])
@login_required
def delete(label_id):
  label = db.session.get(Label, label_id)
  
  # Check if label exists and belongs to the current user
  if not label or label.user_id != current_user.id:
    flash('Label not found or access denied')
    return redirect(url_for('main.dashboard'))
  
  # Check for related transactions before deletion
  if label.transactions.count() > 0:
    flash('Cannot delete label with existing transactions')
    return redirect(url_for('label.detail', label_id=label_id))
  
  db.session.delete(label)
  db.session.commit()
  
  flash('Label deleted successfully')
  return redirect(url_for('main.dashboard'))
