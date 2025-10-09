# root/run.py
"""Application entry point for development server."""
from app import create_app
from app.extensions import db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

# Create database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

if __name__ == "__main__":
    app.run(debug=True)  # Force debug mode on
