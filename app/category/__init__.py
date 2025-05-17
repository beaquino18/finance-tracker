# app/category/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

category = Blueprint('category', __name__, url_prefix='/category')

from app.category import routes
