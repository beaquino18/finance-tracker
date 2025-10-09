# app/auth/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.auth import routes
