"""Initialize Config class to access environment variables."""
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

class Config:
    """Set application configuration."""
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(16))
    
    # Flask-Login settings
    SESSION_TYPE = 'filesystem'
    
    # Application settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
