from flask import Blueprint, jsonify, request
from controllers.api_controller import get_weather_data, get_market_data

api_bp = Blueprint('api', __name__)

@api_bp.route('/weather', methods=['GET'])
def weather():
    location = request.args.get('location', 'Delhi')
    data = get_weather_data(location)
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'Failed to fetch weather data'}), 400

@api_bp.route('/market', methods=['GET'])
def market():
    location = request.args.get('location', 'Delhi')
    data = get_market_data(location)
    if data:
        return jsonify({'success': True, 'data': data})
    return jsonify({'success': False, 'message': 'Failed to fetch market data'}), 400

from controllers.api_controller import add_marketplace_listing, get_marketplace_listings

@api_bp.route('/marketplace/listings', methods=['GET'])
def get_listings():
    listings = get_marketplace_listings()
    return jsonify({'success': True, 'listings': listings})

@api_bp.route('/marketplace/listing', methods=['POST'])
def add_listing():
    data = request.form
    crop_name = data.get('crop_name')
    quantity = data.get('quantity')
    price = data.get('price')
    is_eco = data.get('is_eco', 'false').lower() == 'true'
    
    if 'image' not in request.files or not crop_name or not quantity or not price:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    from werkzeug.utils import secure_filename
    import os
    filename = secure_filename(image_file.filename)
    
    # Save the file to static/uploads
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    upload_dir = os.path.join(base_dir, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    filepath = os.path.join(upload_dir, filename)
    image_file.save(filepath)
    
    # Store relative path for frontend access
    image_url = f"/static/uploads/{filename}"
    
    result = add_marketplace_listing(crop_name, quantity, price, image_url, is_eco)
    return jsonify({'success': True, 'id': result})
