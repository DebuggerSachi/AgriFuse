from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_controller = Blueprint('auth_controller', __name__)

@auth_controller.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
        
    full_name = data.get('full_name')
    mobile_number = data.get('mobile_number')
    password = data.get('password')
    location = data.get('location')
    
    if not all([full_name, mobile_number, password, location]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400
        
    result = AuthService.register_user(full_name, mobile_number, password, location)
    status = result.pop('status')
    return jsonify(result), status

@auth_controller.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing JSON body"}), 400
        
    mobile_number = data.get('mobile_number')
    password = data.get('password')
    
    if not mobile_number or not password:
        return jsonify({"success": False, "message": "Missing credentials"}), 400
        
    result = AuthService.login_user(mobile_number, password)
    status = result.pop('status')
    return jsonify(result), status

@auth_controller.route('/me', methods=['GET'])
@jwt_required()
def me():
    # The identity inside the JWT is typically the user ID as string
    current_user_id = get_jwt_identity()
    result = AuthService.get_user_profile(current_user_id)
    status = result.pop('status')
    return jsonify(result), status
