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
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.homepage'))
        
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        
        # Validate that next_page is safe (prevent open redirect vulnerability)
        if next_page and not is_safe_url(next_page):
            return redirect(url_for('main.homepage'))
            
        return redirect(next_page or url_for('main.homepage'))
        
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
