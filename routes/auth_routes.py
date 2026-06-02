from flask import Blueprint
from controllers.auth_controller import auth_controller

auth_bp = Blueprint('auth_bp', __name__)

# Register the controller commands to the auth blueprint
auth_bp.register_blueprint(auth_controller)
