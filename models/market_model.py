from extensions import db
import datetime

class MarketModel(db.Model):
    __tablename__ = 'market_listings'

    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    is_eco = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create_listing(crop_name, quantity, price, image_path, is_eco=False):
        listing = MarketModel(
            crop_name=crop_name,
            quantity=quantity,
            price=price,
            image_path=image_path,
            is_eco=is_eco
        )
        db.session.add(listing)
        db.session.commit()
        return listing.id

    @staticmethod
    def get_all_listings():
        results = MarketModel.query.order_by(MarketModel.created_at.desc()).all()
        listings = []
        for l in results:
            listings.append({
                "id": l.id,
                "crop_name": l.crop_name,
                "quantity": l.quantity,
                "price": l.price,
                "image_path": l.image_path,
                "is_eco": l.is_eco,
                "created_at": l.created_at.isoformat() if l.created_at else None
            })
        return listings
