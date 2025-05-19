# app/transaction/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

transaction = Blueprint('transaction', __name__)

from app.transaction import routes
