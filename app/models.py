from flask_login import UserMixin
from app.extensions import db
from app.utils import FormEnum

class MonthList(FormEnum):
  JAN = 'January'
  FEB = 'February'
  MAR = 'March'
  APR = 'April'
  MAY = 'May'
  JUN = 'June'
  JUL = 'July'
  AUG = 'August'
  SEP = 'September'
  OCT = 'October'
  NOV = 'November'
  DEC = 'December'
  BLANK = ''
  
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(80), nullable=False)
  email = db.Column(db.String(120), nullable=False, unique=True, index=True)
  password = db.Column(db.String(200), nullable=False)
  profile_image = db.Column(db.String)

class Budget(db.Model):
  """Budget Model"""
  id = db.Column(db.Integer, primary_key=True)
  amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
  month = db.Column(db.Enum(MonthList), default=MonthList.BLANK)
  year = db.Column(db.Integer, nullable=False)
  category = db.relationship('Category')
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
  user = db.relationship('User')
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
  
class Transaction(db.Model):
  
  id = db.Column(db.Integer, primary_key=True)
  amount = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
  description = db.Column(db.String(200))
  date = db.Column(db.Date, nullable=False)
  is_expense = db.Column(db.Boolean, nullable=False)
  # TODO: label
  category = db.relationship('Category')
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
  user = db.relationship('User')
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  
  
class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  color = db.Column(db.String(80), nullable=False)
  icon = db.Column(db.String(80), nullable=False)


class Label(db.Model):
  """Label Model"""
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
  
  # Relationships
  user = db.relationship('User', backref=db.backref('labels', lazy='dynamic'))
