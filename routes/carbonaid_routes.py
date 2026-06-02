from flask import Blueprint
from controllers.carbonaid_controller import (
    carbonaid_landing, farmer_login_page, farmer_register_page,
    industry_login_page, industry_register_page, farmer_dashboard_page,
    industry_dashboard_page, marketplace_page, register_farmer,
    login_farmer, register_industry, login_industry, logout,
    add_activity, buy_credits
)

carbonaid_bp = Blueprint('carbonaid', __name__, url_prefix='/carbonaid')

# Page Routes
@carbonaid_bp.route('/')
def landing():
    return carbonaid_landing()

@carbonaid_bp.route('/farmer/login')
def farmer_login():
    return farmer_login_page()

@carbonaid_bp.route('/farmer/register')
def farmer_register():
    return farmer_register_page()

@carbonaid_bp.route('/industry/login')
def industry_login():
    return industry_login_page()

@carbonaid_bp.route('/industry/register')
def industry_register():
    return industry_register_page()

@carbonaid_bp.route('/farmer/dashboard')
def farmer_dashboard():
    return farmer_dashboard_page()

@carbonaid_bp.route('/industry/dashboard')
def industry_dashboard():
    return industry_dashboard_page()

@carbonaid_bp.route('/marketplace')
def marketplace():
    return marketplace_page()

@carbonaid_bp.route('/logout')
def do_logout():
    return logout()

# API Routes
@carbonaid_bp.route('/api/farmer/register', methods=['POST'])
def api_register_farmer():
    return register_farmer()

@carbonaid_bp.route('/api/farmer/login', methods=['POST'])
def api_login_farmer():
    return login_farmer()

@carbonaid_bp.route('/api/industry/register', methods=['POST'])
def api_register_industry():
    return register_industry()

@carbonaid_bp.route('/api/industry/login', methods=['POST'])
def api_login_industry():
    return login_industry()

@carbonaid_bp.route('/api/activity', methods=['POST'])
def api_add_activity():
    return add_activity()

@carbonaid_bp.route('/api/buy', methods=['POST'])
def api_buy():
    return buy_credits()
