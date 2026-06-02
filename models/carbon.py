from extensions import db
import datetime

class CarbonUser(db.Model):
    __tablename__ = 'carbon_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=True) # for farmers
    email = db.Column(db.String(100), unique=True, nullable=True) # for industries
    location = db.Column(db.String(100), nullable=True)
    industry_type = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False) # 'farmer' or 'industry'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class CarbonActivity(db.Model):
    __tablename__ = 'carbon_activities'
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(100), nullable=False) # mobile for farmer
    farmer_name = db.Column(db.String(100))
    tree_type = db.Column(db.String(100))
    count = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    carbon_kg = db.Column(db.Integer)
    credits = db.Column(db.Float)
    price_per_credit = db.Column(db.Float, default=430.0)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class CarbonPurchase(db.Model):
    __tablename__ = 'carbon_purchases'
    id = db.Column(db.Integer, primary_key=True)
    industry_id = db.Column(db.String(100)) # email for industry
    industry_name = db.Column(db.String(100))
    farmer_id = db.Column(db.String(100))
    farmer_name = db.Column(db.String(100))
    credits = db.Column(db.Float)
    amount = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
