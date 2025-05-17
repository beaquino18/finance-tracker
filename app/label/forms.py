# app/label/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, Length
from app.models import Label

class LabelForm(FlaskForm):
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
