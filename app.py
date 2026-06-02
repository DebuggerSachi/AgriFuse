from flask import Flask, render_template, request, jsonify
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.ai_routes import ai_bp
from routes.carbonaid_routes import carbonaid_bp
from flask_cors import CORS
from extensions import bcrypt, jwt, db
import os
from models.user import UserModel
from models.market_model import MarketModel
from models.dashboard import Monitoring, Breed, DiseaseRecord
from models.carbon import CarbonUser, CarbonActivity, CarbonPurchase

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure SQLite and Session
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agrifuse.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret-farming-key')
    app.secret_key = os.getenv('SECRET_KEY', 'agrifuse-carbon-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(carbonaid_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Internal Server Error'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
