from flask import render_template, request, jsonify, redirect, url_for, session
from extensions import db, bcrypt
import datetime
import uuid
import os
from werkzeug.utils import secure_filename
from models.carbon import CarbonUser, CarbonActivity, CarbonPurchase

# --- Helper Functions ---
def calculate_carbon(tree_count):
    # 1 tree ≈ 22 kg CO2/year
    # 1000 kg CO2 = 1 carbon credit
    co2_kg = int(tree_count) * 22
    credits = co2_kg / 1000.0
    return co2_kg, credits

# --- Page Controllers ---

def carbonaid_landing():
    return render_template('carbonaid/index.html')

def farmer_login_page():
    return render_template('carbonaid/farmer_login.html')

def farmer_register_page():
    return render_template('carbonaid/farmer_register.html')

def industry_login_page():
    return render_template('carbonaid/industry_login.html')

def industry_register_page():
    return render_template('carbonaid/industry_register.html')

def farmer_dashboard_page():
    if 'user_type' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('carbonaid.farmer_login'))
    
    farmer_id = session['user_id']
    activities = CarbonActivity.query.filter_by(user_id=farmer_id).order_by(CarbonActivity.date.desc()).all()
    
    # Calculate totals
    total_trees = sum(item.count for item in activities)
    total_co2 = sum(item.carbon_kg for item in activities)
    total_credits = sum(item.credits for item in activities)
    estimated_earnings = total_credits * 430.0 # Assume ₹430 per credit for mock
    
    return render_template('carbonaid/farmer_dashboard.html', 
                          farmer=session.get('user_name'),
                          stats={
                              'trees': total_trees,
                              'co2': total_co2,
                              'credits': round(total_credits, 2),
                              'earnings': round(estimated_earnings, 2)
                          },
                          activities=activities)

def industry_dashboard_page():
    if 'user_type' not in session or session['user_type'] != 'industry':
        return redirect(url_for('carbonaid.industry_login'))
    
    industry_id = session['user_id']
    purchases = CarbonPurchase.query.filter_by(industry_id=industry_id).order_by(CarbonPurchase.date.desc()).all()
    
    total_purchased = sum(item.credits for item in purchases)
    offset = total_purchased * 1000 # 1 credit = 1000kg CO2
    
    return render_template('carbonaid/industry_dashboard.html',
                          industry=session.get('user_name'),
                          stats={
                              'purchased': round(total_purchased, 2),
                              'offset': round(offset, 2)
                          },
                          purchases=purchases)

def marketplace_page():
    # Marketplace shows all available credits from farmers
    listings = CarbonActivity.query.filter(CarbonActivity.credits > 0).all()
    return render_template('carbonaid/marketplace.html', listings=listings)

# --- API Controllers ---

def register_farmer():
    data = request.json
    name = data.get('name')
    mobile = data.get('mobile')
    location = data.get('location')
    password = data.get('password')

    if not all([name, mobile, location, password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if CarbonUser.query.filter_by(mobile=mobile).first():
        return jsonify({'success': False, 'message': 'Mobile number already registered'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = CarbonUser(
        name=name,
        mobile=mobile,
        location=location,
        password=hashed_password,
        user_type='farmer'
    )
    
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Registration successful'})

def login_farmer():
    data = request.json
    mobile = data.get('mobile')
    password = data.get('password')

    user = CarbonUser.query.filter_by(mobile=mobile, user_type='farmer').first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = mobile
        session['user_name'] = user.name
        session['user_type'] = 'farmer'
        return jsonify({'success': True, 'redirect': url_for('carbonaid.farmer_dashboard')})
    
    return jsonify({'success': False, 'message': 'Invalid mobile or password'}), 401

def register_industry():
    data = request.json
    company_name = data.get('company_name')
    industry_type = data.get('industry_type')
    email = data.get('email')
    password = data.get('password')

    if not all([company_name, industry_type, email, password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if CarbonUser.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    user = CarbonUser(
        name=company_name,
        email=email,
        industry_type=industry_type,
        password=hashed_password,
        user_type='industry'
    )
    
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Registration successful'})

def login_industry():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = CarbonUser.query.filter_by(email=email, user_type='industry').first()
    
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = email
        session['user_name'] = user.name
        session['user_type'] = 'industry'
        return jsonify({'success': True, 'redirect': url_for('carbonaid.industry_dashboard')})
    
    return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

def logout():
    session.clear()
    return redirect(url_for('carbonaid.landing'))

def add_activity():
    if 'user_type' not in session or session['user_type'] != 'farmer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    tree_type = request.form.get('tree_type')
    count_str = request.form.get('count')
    
    if not tree_type or not count_str:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    count = int(count_str)
    
    # Handle File Upload
    image_url = 'https://via.placeholder.com/150'
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            # Use a path within static/uploads
            base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            upload_folder = os.path.join(base_dir, 'static', 'uploads', 'carbonaid')
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            image_url = f"/static/uploads/carbonaid/{filename}"

    co2, credits = calculate_carbon(count)
    
    activity = CarbonActivity(
        id=str(uuid.uuid4()),
        user_id=session['user_id'],
        farmer_name=session['user_name'],
        tree_type=tree_type,
        count=count,
        image_url=image_url,
        carbon_kg=co2,
        credits=credits,
        price_per_credit=430.0
    )
    
    db.session.add(activity)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Activity logged and credits listed!'})

def buy_credits():
    if 'user_type' not in session or session['user_type'] != 'industry':
        return jsonify({'success': False, 'message': 'Only industries can buy credits'}), 401
    
    data = request.json
    activity_id = data.get('activity_id')
    
    activity = CarbonActivity.query.get(activity_id)
    if not activity or activity.credits <= 0:
        return jsonify({'success': False, 'message': 'Credits no longer available'}), 400
    
    # Record purchase
    purchase = CarbonPurchase(
        industry_id=session['user_id'],
        industry_name=session['user_name'],
        farmer_id=activity.user_id,
        farmer_name=activity.farmer_name,
        credits=activity.credits,
        amount=activity.credits * activity.price_per_credit,
        image_url=activity.image_url
    )
    
    db.session.add(purchase)
    
    # Remove credits from marketplace (update activity)
    activity.credits = 0
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Credits purchased successfully!'})
