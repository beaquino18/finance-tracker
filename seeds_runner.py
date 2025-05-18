from app import create_app
from app.extensions import db
from app.seeds import seed_database

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_database()
