from extensions import db
from models.dashboard import Monitoring, Breed, DiseaseRecord
from sqlalchemy import func
import datetime
import random

class DashboardService:
    @staticmethod
    def seed_data_if_empty():
        # Check if DB is empty and add some seed data for demo
        try:
            if Monitoring.query.count() == 0:
                for i in range(30):
                    date = datetime.datetime.utcnow() - datetime.timedelta(days=30-i)
                    temp = random.uniform(20, 35)
                    humid = random.uniform(40, 80)
                    moist = random.uniform(30, 90)
                    m = Monitoring(date=date, temperature=temp, humidity=humid, soil_moisture=moist)
                    db.session.add(m)
                    
                breeds = [
                    ("Gir", 15), ("Sahiwal", 12), ("Red Sindhi", 10), 
                    ("Murrah", 8), ("Jaffrabadi", 14), ("Jamunapari", 2),
                    ("Beetal", 1.5), ("Sirohi", 1.2)
                ]
                for name, milk in breeds:
                    b = Breed(breed_name=name, milk_production=milk)
                    db.session.add(b)
                
                diseases = ["Wheat Rust", "Rice Blast", "Potato Blight", "Cotton Bollworm", "Maize Smut"]
                for i in range(25):
                    crop = random.choice(["Wheat", "Rice", "Potato", "Cotton", "Maize"])
                    disease = random.choice(diseases)
                    dr = DiseaseRecord(crop_name=crop, disease_name=disease)
                    db.session.add(dr)
                
                db.session.commit()
        except:
            db.session.rollback()

    @staticmethod
    def get_monitoring_trends():
        # Auto-seed if needed
        DashboardService.seed_data_if_empty()
        
        # Fetch last 30 days
        data = Monitoring.query.order_by(Monitoring.date.asc()).limit(30).all()
        
        labels = [d.date.strftime("%d %b") if d.date else "" for d in data]
        temperatures = [round(d.temperature, 2) for d in data]
        humidities = [round(d.humidity, 2) for d in data]
        soil_moistures = [round(d.soil_moisture, 2) for d in data]
        
        return {
            "success": True,
            "data": {
                "labels": labels,
                "temperatures": temperatures,
                "humidities": humidities,
                "soil_moistures": soil_moistures
            },
            "status": 200
        }
        
    @staticmethod
    def get_breed_comparisons():
        DashboardService.seed_data_if_empty()
        
        breeds = Breed.query.all()
        labels = [b.breed_name for b in breeds]
        milk = [b.milk_production for b in breeds]
        
        return {
            "success": True,
            "data": {
                "labels": labels,
                "milk_production": milk
            },
            "status": 200
        }

    @staticmethod
    def get_disease_stats():
        DashboardService.seed_data_if_empty()
        
        # Group by crop_name
        stats = db.session.query(
            DiseaseRecord.crop_name, 
            func.count(DiseaseRecord.id)
        ).group_by(DiseaseRecord.crop_name).all()
        
        labels = [s[0] for s in stats]
        counts = [s[1] for s in stats]
        
        return {
            "success": True,
            "data": {
                "labels": labels,
                "counts": counts
            },
            "status": 200
        }
