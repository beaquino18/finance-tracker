# app/__init__.py
"""Initialize the application."""
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, bcrypt

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Register blueprints
    from app.auth.routes import auth as auth_blueprint
    from app.wallet.routes import wallet as wallet_blueprint
    from app.budget.routes import budget as budget_blueprint
    from app.transaction.routes import transaction as transaction_blueprint
    from app.category.routes import category as category_blueprint
    from app.label.routes import label as label_blueprint
    from app.main.routes import main as main_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(wallet_blueprint)
    app.register_blueprint(budget_blueprint)
    app.register_blueprint(transaction_blueprint)
    app.register_blueprint(category_blueprint)
    app.register_blueprint(label_blueprint)
    app.register_blueprint(main_blueprint)
    
    # Setup user loader for Flask-Login
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app
