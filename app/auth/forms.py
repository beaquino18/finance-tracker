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
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('No user with that email. Please try again.')
    
    def validate_password(self, password):
        user = User.query.filter_by(email=self.email.data).first()
        if user and not bcrypt.check_password_hash(
            user.password, password.data):
            raise ValidationError('Password doesn\'t match. Please try again.')
