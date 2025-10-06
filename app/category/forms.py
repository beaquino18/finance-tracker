# app/category/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, ValidationError
from wtforms.validators import DataRequired, Length
from app.models import Category

class CategoryForm(FlaskForm):
    """Form for adding, updating and deleting a category"""
    name = StringField('Category Name', validators=[
        DataRequired(),
        Length(min=3, max=50, message="Category name must be between 3 to 50 chars")
    ])
    # Changed to HiddenField - will be set via JavaScript
    color = HiddenField('Color', validators=[DataRequired()])
    icon = HiddenField('Icon', validators=[DataRequired()])
    
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
