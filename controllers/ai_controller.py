import os
import logging
from services.api_service import predict_crop_disease

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def predict_disease(image_path):
    """
    Calls the Kindwise API and returns a rich result dictionary.
    The result contains status, disease name, confidence, description,
    categorized treatments, severity, similar images, and Hindi translations.
    """
    logger.info(f"Calling Kindwise API for image: {image_path}")
    
    result = predict_crop_disease(image_path)
    
    # Handle error or low-confidence cases
    if result.get('status') in ['error', 'low_confidence']:
        return result
    
    return result
