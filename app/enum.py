from enum import Enum

class FormEnum(Enum):
    """Helper class to make it easier to use enums with forms."""
    @classmethod
    def choices(cls):
        return [(choice.name, choice.value) for choice in cls]

    def __str__(self):
        return str(self.value)

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
  
class Color(FormEnum):
    ORANGE_RED = '#BB3E00'  # Your specified color
    BLUE = '#4A90E2'        # Professional blue
    GREEN = '#50E3C2'       # Mint green for cash
    PURPLE = '#BD10E0'      # Credit card purple
    GOLD = '#F5A623'        # Gold for savings
    NAVY = '#2E3A59'        # Navy for checking
    TEAL = '#4ECDC4'        # Teal for digital
    GRAY = '#95A5A6'        # Gray for other
    RED = '#E74C3C'         # Red for credit
    INDIGO = '#5E72E4'      # Indigo for investment
    BLACK = '#2C3E50'       # Black for premium
    EMERALD = '#27AE60'     # Emerald for positive balance

class CategoryIcon(FormEnum):
    # Finance & Shopping
    SHOPPING_CART = "fa-shopping-cart"
    CREDIT_CARD = "fa-credit-card"
    DOLLAR_SIGN = "fa-dollar-sign"
    WALLET = "fa-wallet"
    PIGGY_BANK = "fa-piggy-bank"
    
    # Food & Dining
    UTENSILS = "fa-utensils"
    COFFEE = "fa-coffee"
    PIZZA_SLICE = "fa-pizza-slice"
    BEER = "fa-beer"
    
    # Transportation
    CAR = "fa-car"
    BUS = "fa-bus"
    TRAIN = "fa-train"
    PLANE = "fa-plane"
    BICYCLE = "fa-bicycle"
    GAS_PUMP = "fa-gas-pump"
    
    # Home & Utilities
    HOME = "fa-home"
    LIGHTBULB = "fa-lightbulb"
    TOOLS = "fa-tools"
    COUCH = "fa-couch"
    
    # Health & Fitness
    HEARTBEAT = "fa-heartbeat"
    PILLS = "fa-pills"
    DUMBBELL = "fa-dumbbell"
    HOSPITAL = "fa-hospital"
    
    # Entertainment
    FILM = "fa-film"
    MUSIC = "fa-music"
    GAMEPAD = "fa-gamepad"
    BOOK = "fa-book"
    
    # Personal
    GIFT = "fa-gift"
    TSHIRT = "fa-tshirt"
    CUT = "fa-cut"
    GRADUATION_CAP = "fa-graduation-cap"
    
    # Business & Work
    BRIEFCASE = "fa-briefcase"
    LAPTOP = "fa-laptop"
    CHART_LINE = "fa-chart-line"
    
    # Other
    QUESTION_CIRCLE = "fa-question-circle"
    STAR = "fa-star"
    TAG = "fa-tag"
    
    @classmethod
    def choices(cls):
        return [(icon.value, icon.name.replace('_', ' ').title()) for icon in cls]
