# app/wallet/__init__.py
"""Authentication blueprint package."""
from flask import Blueprint

wallet = Blueprint('wallet', __name__, url_prefix='/wallet')

from app.wallet import routes
