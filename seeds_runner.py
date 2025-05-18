"""Scripts to run seeds.py"""
from app import create_app
from app.seeds import seed_database

if __name__ == "__main__":
  app = create_app()
  with app.app_context():
    seed_database()
