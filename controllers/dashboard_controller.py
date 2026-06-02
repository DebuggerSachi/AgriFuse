from flask import Blueprint, jsonify
from services.dashboard_service import DashboardService

dashboard_controller = Blueprint('dashboard_controller', __name__)

@dashboard_controller.route('/monitoring', methods=['GET'])
def monitoring_data():
    result = DashboardService.get_monitoring_trends()
    status = result.pop('status')
    return jsonify(result), status

@dashboard_controller.route('/breeds', methods=['GET'])
def breed_comparisons():
    result = DashboardService.get_breed_comparisons()
    status = result.pop('status')
    return jsonify(result), status

@dashboard_controller.route('/diseases', methods=['GET'])
def disease_stats():
    result = DashboardService.get_disease_stats()
    status = result.pop('status')
    return jsonify(result), status
