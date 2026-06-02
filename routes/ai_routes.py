from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
from controllers.ai_controller import predict_disease

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/predict-disease', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Create temp_uploads within instance directory
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        temp_dir = os.path.join(base_dir, 'instance', 'temp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        try:
            result = predict_disease(filepath)
            os.remove(filepath)
            
            # Handle error responses
            if result.get('status') == 'error':
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Analysis failed.'),
                    'message_hi': result.get('message_hi', 'विश्लेषण विफल रहा।')
                }), 400
            
            # Handle low confidence
            if result.get('status') == 'low_confidence':
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'Low confidence detection.'),
                    'message_hi': result.get('message_hi', 'कम विश्वास स्तर।'),
                    'confidence': result.get('confidence', 0)
                }), 400

            # Success - return the full rich response
            return jsonify({
                'success': True,
                'disease': result.get('disease_name', 'Unknown'),
                'confidence': result.get('confidence', 0),
                'description': result.get('description', ''),
                'description_hi': result.get('description_hi', ''),
                'common_names': result.get('common_names', []),
                'treatments': result.get('treatments', {}),
                'treatment_combined': result.get('treatment_combined', ''),
                'severity': result.get('severity', 'Unknown'),
                'similar_images': result.get('similar_images', []),
                'alternatives': result.get('alternatives', []),
                'external_url': result.get('external_url', '')
            })
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'message': str(e)}), 500
