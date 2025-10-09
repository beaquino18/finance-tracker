from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
from app.enum import MonthList

class BudgetForm(FlaskForm):
  """Form for adding/updating/deleting a Budget"""
  # Generate year choices dynamically
  current_year = datetime.now().year
  year_choices = [(str(year), str(year)) for year in range(current_year - 5, current_year + 6)]
  
  amount = DecimalField('Amount', places=2, validators=[
                DataRequired(),
                NumberRange(min=0.01, max=99999999.99, message="Amount must be between 0.01 and 99,999,999.99")])
  month = SelectField('Month', choices=MonthList.choices(), coerce=lambda name: MonthList[name], validators=[DataRequired()])
  year = SelectField('Year', choices=year_choices, validators=[DataRequired()])
  category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
  wallet_id = SelectField('Wallet', coerce=int, validators=[DataRequired()])
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
