# app/label/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

label = Blueprint('label', __name__, url_prefix='/label')

from app.label import routes
