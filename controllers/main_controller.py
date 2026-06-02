from flask import render_template
from services.main_service import get_dashboard_data

def get_home_page():
    dashboard_data = get_dashboard_data()
    return render_template('index.html', data=dashboard_data)
