from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.fields import DateField
from datetime import date
from app.models import Label

class TransactionForm(FlaskForm):
  """Form for adding/updating/deleting a Transaction"""
  amount = DecimalField('Amount', places=2, validators=[
              DataRequired(),
              NumberRange(min=0.01, max=99999999.99, message="Amount must be between 0.01 and 99,999,999.99")])
  description = StringField('Description', validators=[
                    Optional(),
                    Length(max=200, message="Description must be 200 chars or less")])
  date = DateField('Date', format='%Y-%m-%d', validators=[
              DataRequired()], default=date.today)
  is_expense = BooleanField('Is Expense', default=True)
  category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
  wallet_id = SelectField('Wallet', coerce=int, validators=[DataRequired()])
  labels = QuerySelectMultipleField('Labels', query_factory=lambda: Label.query, 
              get_label='name', validators=[Optional()])
  
  # Dynamically populate dropdown choices based on current user
  # Without this , all users would see everyone's labels in the dropdowns 
  def __init__(self, *args, **kwargs):
    # 1. Call the parent class constructor first
    super().__init__(*args, **kwargs)
    
    # 2. Check if 'user' was passed as a keyword argument
    if 'user' in kwargs:
      # 3. Remove 'user' from kwargs and store it
      user = kwargs.pop('user')
      
      # 4. Set the choices for category dropdown
      # Only show active categories belonging to this user
      self.category_id.choices = [(c.id, c.name) for c in user.categories.filter_by(is_active=True)]
      
      # 5. Set the choices for wallet dropdown
      # Only show active wallets belonging to this user
      self.wallet_id.choices = [(w.id, w.name) for w in user.wallets.filter_by(is_active=True)]
      
      # 6. Set the query factory for labels
      # This tells QuerySelectMultipleField to only query labels for this user
      self.labels.query_factory = lambda: Label.query.filter_by(user_id=user.id)

