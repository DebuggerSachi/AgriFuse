from extensions import db
import datetime

class Monitoring(db.Model):
    __tablename__ = 'monitoring'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    soil_moisture = db.Column(db.Float)

class Breed(db.Model):
    __tablename__ = 'breeds'
    id = db.Column(db.Integer, primary_key=True)
    breed_name = db.Column(db.String(100))
    milk_production = db.Column(db.Float)

class DiseaseRecord(db.Model):
    __tablename__ = 'disease_records'
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100))
    disease_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
