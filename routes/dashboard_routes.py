from flask import Blueprint
from controllers.dashboard_controller import dashboard_controller

dashboard_bp = Blueprint('dashboard_bp', __name__)

dashboard_bp.register_blueprint(dashboard_controller)
