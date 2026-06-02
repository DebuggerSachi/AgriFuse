from extensions import bcrypt, jwt
from models.user import UserModel
from flask_jwt_extended import create_access_token
import datetime

class AuthService:
    @staticmethod
    def register_user(full_name, mobile_number, password, location):
        if UserModel.find_by_mobile(mobile_number):
            return {"success": False, "message": "Mobile number already registered", "status": 400}
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        UserModel.create_user(
            full_name=full_name,
            mobile_number=mobile_number,
            password_hash=hashed_password,
            location=location
        )
        
        return {"success": True, "message": "User registered successfully", "status": 201}

    @staticmethod
    def login_user(mobile_number, password):
        user = UserModel.find_by_mobile(mobile_number)
        
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return {"success": False, "message": "Invalid mobile number or password", "status": 401}
            
        access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(days=7))
        return {
            "success": True, 
            "message": "Login successful", 
            "token": access_token, 
            "user": {
                "id": str(user.id),
                "full_name": user.full_name,
                "mobile_number": user.mobile_number,
                "location": user.location,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "status": 200
        }

    @staticmethod
    def get_user_profile(user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"success": False, "message": "User not found", "status": 404}
            
        return {
            "success": True, 
            "user": {
                "id": str(user.id),
                "full_name": user.full_name,
                "mobile_number": user.mobile_number,
                "location": user.location,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }, 
            "status": 200
        }
