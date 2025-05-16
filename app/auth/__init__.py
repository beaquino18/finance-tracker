# app/auth/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')

from app.auth import routes
