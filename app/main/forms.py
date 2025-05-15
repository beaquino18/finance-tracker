from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, BooleanField, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.fields import DateField
from datetime import datetime
from app.enum import MonthList, Color, CategoryIcon
from app.models import Budget, Wallet, Transaction, Label, Category
from datetime import date


class WalletForm(FlaskForm):
  """Form for adding/updating/deleting a Wallet"""
  name = StringField('Wallet Name', validators=[
            DataRequired(),
            Length(min=3, max=80, message="Wallet name needs to be between 3 and 80 chars")])
  balance = DecimalField('Initial Balance', places=2, validators=[
                DataRequired(),
                NumberRange(min=-99999999.99, max=99999999.99)],
                    default=0.00)
  color = SelectField('Color', choices=Color.choices(), validators=[
                DataRequired()],
                coerce=lambda name: Color[name])
  is_active = BooleanField('Active', default=True)
  
class BudgetForm(FlaskForm):
  """Form for adding/updating/deleting a Budget"""
  # Generate year choices dynamically
  current_year = datetime.now().year
  year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 6)]
  
  amount = DecimalField('Amount', validators=[DataRequired()])
  month = SelectField('Month', choices=[(m.name, m.value) for m in MonthList], validators=[DataRequired()])
  year = SelectField('Year', choices=year_choices, validators=[DataRequired()])
  category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
  wallet_id = SelectField('Wallet', coerce=int, validators=[DataRequired()])
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

class Transaction(FlaskForm):
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


class Label(FlaskForm):
  """Form for adding, updating, and deleting labels"""
  name = StringField('Label Name', validators=[
            DataRequired(),
            Length(min=3, max=50, message="Label name must be between 3 to 50 chars")])
  
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    self.edit_label = kwargs.pop('edit_label', None)
    super().__init__(*args, **kwargs)
  
  # Custom validator to ensure label name is unique per user  
  def validate_name(self, field):
    if self.user:
      query = Label.query.filter_by(
        name=field.data,
        user_id=self.user.id
      )
      
      # If editing, exclude current label from uniqueness check
      if self.edit_label:
        query = query.filter(Label.id != self.edit_label.id)
        
      if query.first():
        raise ValidationError(f"You already have a label named '{field.data}'")


class Category(FlaskForm):
  """Form for adding, updating and deleting a category"""
  name = StringField('Label Name', validators=[
            DataRequired(),
            Length(min=3, max=50, message="Category name must be between 3 to 50 chars")])
  color = SelectField('Color', choices=Color.choices(), validators=[
              DataRequired()],
              coerce=lambda name: Color[name])
  icon = SelectField('Icon', choices=CategoryIcon.choices(), 
              validators=[DataRequired()])
  
  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    self.edit_category = kwargs.pop('edit_category', None)
    super().__init__(*args, **kwargs)

    def validate_name(self, field):
        """Ensure category name is unique per user"""
        if self.user:
            query = Category.query.filter_by(
                name=field.data,
                user_id=self.user.id
            )
            
            if self.edit_category:
                query = query.filter(Category.id != self.edit_category.id)
            
            if query.first():
                raise ValidationError(f"You already have a category named '{field.data}'")  
    
