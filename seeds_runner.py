# seeds_runner.py
"""Script to run database seeding."""
from app import create_app
from app.extensions import db
from app.seeds import seed_database

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("Dropping all existing tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        print("Running seed database function...")
        seed_database()
        
        print("Database setup and seeding completed successfully!")
