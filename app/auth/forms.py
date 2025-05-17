# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, URL, Optional
from app.models import User
from app.extensions import bcrypt

class SignUpForm(FlaskForm):
    first_name = StringField('First Name',
      validators=[DataRequired(), Length(min=3, max=50)])
    last_name = StringField('Last Name',
      validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email',
        validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    profile_image = StringField('Profile Image URL', 
        validators=[Optional(), URL()],
        description="Optional: URL to your profile image")
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
    
    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('No user with that email')
            return False
        
        if not bcrypt.check_password_hash(user.password, self.password.data):
            self.password.errors.append('Invalid password')
            return False
        
        return True
