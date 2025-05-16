# app/budget/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

budget = Blueprint('budget', __name__, url_prefix='/budget')

from app.budget import routes
