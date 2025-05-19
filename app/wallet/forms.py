# app/wallet/forms.py
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange

class WalletForm(FlaskForm):
  """Form for adding/updating/deleting a Wallet"""
  name = StringField('Wallet Name', validators=[
            DataRequired(),
            Length(min=3, max=80, message="Wallet name needs to be between 3 and 80 chars")])
  balance = DecimalField('Initial Balance', places=2, validators=[
                DataRequired(),
                NumberRange(min=-99999999.99, max=99999999.99)],
                    default=0.00)
  is_active = BooleanField('Active', default=True)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
