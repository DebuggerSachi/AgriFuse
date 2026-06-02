from extensions import db
import datetime

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def create_user(full_name, mobile_number, password_hash, location):
        new_user = UserModel(
            full_name=full_name,
            mobile_number=mobile_number,
            password_hash=password_hash,
            location=location
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def find_by_mobile(mobile_number):
        return UserModel.query.filter_by(mobile_number=mobile_number).first()

    @staticmethod
    def find_by_id(user_id):
        return UserModel.query.get(int(user_id))
