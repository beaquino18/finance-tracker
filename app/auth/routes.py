# app/auth/routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
from app.models import User
from app.auth.forms import SignUpForm, LoginForm
from app.extensions import db, bcrypt

auth = Blueprint("auth", __name__)

# Helper function to check if URL is safe for redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
        
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Set profile image if none provided
        profile_image = form.profile_image.data if form.profile_image.data else "/static/images/default_avatar.png"
        
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            profile_image=profile_image,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Account Created Successfully.')
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with error handling and logging."""
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            # Get user by email
            user = User.query.filter_by(email=form.email.data).first()
            
            # Check if user exists
            if not user:
                flash('No user found with that email', 'danger')
                return render_template('login.html', form=form)
            
            # Check password (this is also done in form validation but adds extra check)
            if not bcrypt.check_password_hash(user.password, form.password.data):
                flash('Invalid password', 'danger')
                return render_template('login.html', form=form)
            
            # Login the user
            login_user(user, remember=True)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Get the next page or default to homepage
            next_page = request.args.get('next')
            
            # Validate next_page is safe (prevent open redirect vulnerability)
            if next_page and not is_safe_url(next_page):
                return redirect(url_for('main.homepage'))
                
            return redirect(next_page or url_for('main.homepage'))
            
        except Exception as e:
            # Log the error for debugging
            import traceback
            error_details = traceback.format_exc()
            print(f"Login Error: {str(e)}")
            print(error_details)
            
            # Flash a user-friendly message
            flash('An error occurred during login. Please try again.', 'danger')
            return render_template('login.html', form=form)
    
    # If GET request or form validation failed, display the login form
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
