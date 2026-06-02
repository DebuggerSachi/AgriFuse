from flask import Blueprint

main_bp = Blueprint('main', __name__)

from controllers.main_controller import get_home_page

@main_bp.route('/')
def home():
    return get_home_page()
