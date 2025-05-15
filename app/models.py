from flask_login import UserMixin
from app.extensions import db
from app.enum import Color, MonthList, CategoryIcon
from datetime import datetime

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), nullable=False, unique=True, index=True)
  password = db.Column(db.String(200), nullable=False)
  profile_image = db.Column(db.String(200))
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  
  def __repr__(self):
    return f'<User {self.email}>'
  
class Wallet(db.Model):
    """Wallet Model - represents user's accounts/payment methods"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)  # e.g. "Chase Checking", "Cash", "Amex"
    balance = db.Column(db.Numeric(precision=10, scale=2), nullable=False, default=0.00)
    color = db.Column(db.Enum(Color), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # To hide/show wallets
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    user = db.relationship('User', backref=db.backref('wallets', lazy='dynamic'))
    
    # Make wallet names unique per user
    __table_args__ = (
        db.UniqueConstraint('name', 'user_id', name='unique_wallet_per_user'),
    )
    
    def __repr__(self):
        return f'<Wallet {self.name}: {self.balance}>'


class Budget(db.Model):
  """Budget Model"""
  id = db.Column(db.Integer, primary_key=True)
  amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
  month = db.Column(db.Enum(MonthList), default=MonthList.BLANK)
  year = db.Column(db.Integer, nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
  
  #Relationships
  category = db.relationship('Category', backref=db.backref('budgets', lazy='dynamic'))
  user = db.relationship('User', backref=db.backref('budgets', lazy='dynamic'))
  wallet = db.relationship('Wallet',
            backref=db.backref('budgets', lazy='dynamic'))
  
  def __repr__(self):
        return f'<Budget {self.amount} for {self.month.value} {self.year}>'
  
"""Join Table for Many to Many Relationships for Transactions and labels"""  
transaction_labels = db.Table('transaction_labels',
      db.Column('transaction_id', db.Integer, db.ForeignKey('transaction.id'), primary_key=True),
      db.Column('label_id', db.Integer, db.ForeignKey('label.id'), primary_key=True))

class Transaction(db.Model):  
  id = db.Column(db.Integer, primary_key=True)
  amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
  description = db.Column(db.String(200))
  date = db.Column(db.Date, nullable=False)
  is_expense = db.Column(db.Boolean, nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
  
  # Relationships of Transaction
  category = db.relationship('Category')
  user = db.relationship('User')
  labels = db.relationship('Label', 
              secondary='transaction_labels',
              backref=db.backref('transactions', lazy='dynamic'))
  wallet = db.relationship('Wallet',
              backref=db.backref('transactions', lazy='dynamic'))
  
  def __repr__(self):
    return f'<Transaction {self.amount} on {self.date}>'
  
class Label(db.Model):
  """Label Model"""
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  
  # Relationships
  user = db.relationship('User', backref=db.backref('labels', lazy='dynamic'))
  
  """
  Ensure label names are unique per user
    Example:
    User A = creates label 'visa'
    User B = creates label 'visa'
    User A won't be allowed to create another label called visa
      
  """
  __table_args__ = (
    db.UniqueConstraint('name', 'user_id', name='unique_label_per_user')
  )

  def __repr__(self):
      return f'<Label {self.name}>'

  
class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  color = db.Column(db.Enum(Color), nullable=False)
  icon = db.Column(db.String(80), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
    # Relationships
  user = db.relationship('User', backref=db.backref('categories', lazy='dynamic'))
  
  # Make category names unique per user
  __table_args__ = (
      db.UniqueConstraint('name', 'user_id', name='unique_category_per_user'),
  )

  def __repr__(self):
    return f'<Category {self.name}>'
