import requests
import json

def fetch_weather_data(location):
    try:
        # We can use Open-Meteo API as it doesn't require an API key
        # First we need to get coordinates for the location
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
        geocode_response = requests.get(geocode_url)
        if geocode_response.status_code == 200:
            geocode_data = geocode_response.json()
            if 'results' in geocode_data and len(geocode_data['results']) > 0:
                lat = geocode_data['results'][0]['latitude']
                lon = geocode_data['results'][0]['longitude']
                name = geocode_data['results'][0]['name']
                
                # Now fetch weather for these coordinates
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=relative_humidity_2m"
                weather_response = requests.get(weather_url)
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    current = weather_data.get('current_weather', {})
                    
                    # humidity from the closest hour
                    humidity = "N/A"
                    if 'hourly' in weather_data and 'relative_humidity_2m' in weather_data['hourly']:
                        humidity = str(weather_data['hourly']['relative_humidity_2m'][0]) + "%"
                        
                    return {
                        'location': name,
                        'temperature': f"{current.get('temperature', '--')}°C",
                        'windspeed': f"{current.get('windspeed', '--')} km/h",
                        'humidity': humidity,
                        'condition': get_weather_description(current.get('weathercode', 0))
                    }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        
    return None

def get_weather_description(code):
    # WMO Weather interpretation codes (WW)
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light",
        53: "Drizzle: Moderate",
        55: "Drizzle: Dense",
        56: "Freezing Drizzle: Light",
        57: "Freezing Drizzle: Dense",
        61: "Rain: Slight",
        63: "Rain: Moderate",
        65: "Rain: Heavy",
        66: "Freezing Rain: Light",
        67: "Freezing Rain: Heavy",
        71: "Snow fall: Slight",
        73: "Snow fall: Moderate",
        75: "Snow fall: Heavy",
        77: "Snow grains",
        80: "Rain showers: Slight",
        81: "Rain showers: Moderate",
        82: "Rain showers: Violent",
        85: "Snow showers slight",
        86: "Snow showers heavy",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown")

def predict_crop_disease(image_path):
    """
    Calls the Kindwise Crop Health API to identify plant diseases.
    Returns a rich dictionary with disease name, confidence, description,
    categorized treatments (biological, chemical, prevention), and Hindi translations.
    """
    import base64
    import os
    try:
        api_key = os.getenv("KINDWISE_CROP_API_KEY")
        if not api_key:
            return {"status": "error", "error_type": "Error", "message": "API Key not found.", "message_hi": "API कुंजी नहीं मिली।"}

        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            img_data = f"data:image/jpeg;base64,{encoded_string}"

        url = "https://crop.kindwise.com/api/v1/identification"
        headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "images": [img_data],
            "similar_images": True
        }
        
        # Request extra detail fields: description, treatment, common_names, url
        # Also request Hindi language alongside English
        params = {
            "details": "description,treatment,common_names,url,severity",
            "language": "en,hi"
        }
        
        res = requests.post(url, json=payload, headers=headers, params=params)
        
        if res.status_code == 201:
            data = res.json()
            
            if data and data.get('result') and data['result'].get('disease'):
                disease_info = data['result']['disease']
                
                if disease_info.get('suggestions') and len(disease_info['suggestions']) > 0:
                    top_suggestion = disease_info['suggestions'][0]
                    disease_name = top_suggestion.get('name', 'Unknown')
                    probability = top_suggestion.get('probability', 0)
                    
                    # --- CONFIDENCE CHECK (70% threshold) ---
                    if probability < 0.7:
                        return {
                            "status": "low_confidence",
                            "error_type": "LOW_CONFIDENCE",
                            "message": "The image confidence is too low. Please upload a clearer leaf image with better lighting.",
                            "message_hi": "छवि का विश्वास स्तर बहुत कम है। कृपया बेहतर रोशनी के साथ एक स्पष्ट पत्ती की छवि अपलोड करें।",
                            "confidence": round(probability * 100, 1)
                        }
                    
                    # --- Extract details ---
                    details = top_suggestion.get('details', {})
                    
                    # Description (English + Hindi)
                    description_en = ""
                    description_hi = ""
                    desc_data = details.get('description', {})
                    if isinstance(desc_data, dict):
                        # Could be wiki_description or value
                        description_en = desc_data.get('value', desc_data.get('wiki_description', ''))
                        if not description_en and isinstance(desc_data, str):
                            description_en = desc_data
                    elif isinstance(desc_data, str):
                        description_en = desc_data
                    
                    # Try to get Hindi description from language_details or localized fields
                    lang_details = details.get('language_details', {})
                    if isinstance(lang_details, dict) and 'hi' in lang_details:
                        hi_data = lang_details['hi']
                        if isinstance(hi_data, dict):
                            description_hi = hi_data.get('description', {}).get('value', '')
                    
                    # Common names
                    common_names = details.get('common_names', [])
                    if common_names is None:
                        common_names = []
                    
                    # External URL
                    ext_url = details.get('url', '')
                    
                    # Severity
                    severity = details.get('severity', '')
                    
                    # Treatment - categorized into biological, chemical, prevention
                    treatment_data = details.get('treatment', {})
                    treatments = {
                        'biological': [],
                        'chemical': [],
                        'prevention': []
                    }
                    treatment_combined = ""
                    
                    if isinstance(treatment_data, dict):
                        for method_key, method_val in treatment_data.items():
                            key_lower = method_key.lower()
                            if isinstance(method_val, list):
                                items = method_val
                            elif isinstance(method_val, str):
                                items = [method_val]
                            else:
                                items = []
                            
                            if 'bio' in key_lower:
                                treatments['biological'].extend(items)
                            elif 'chem' in key_lower:
                                treatments['chemical'].extend(items)
                            elif 'prev' in key_lower:
                                treatments['prevention'].extend(items)
                            else:
                                # Put unclassified methods into prevention
                                treatments['prevention'].extend(items)
                        
                        # Build a combined treatment string as fallback
                        all_items = []
                        for cat_items in treatments.values():
                            all_items.extend(cat_items)
                        if all_items:
                            treatment_combined = " ".join(all_items)
                    
                    if not treatment_combined:
                        treatment_combined = "No specific treatment information available."
                    
                    # Similar images
                    similar_images = top_suggestion.get('similar_images', [])
                    similar_img_urls = []
                    if similar_images:
                        for sim_img in similar_images[:3]:
                            if isinstance(sim_img, dict) and sim_img.get('url'):
                                similar_img_urls.append(sim_img['url'])
                    
                    # Alternative suggestions (2nd and 3rd)
                    alternatives = []
                    for alt in disease_info['suggestions'][1:4]:
                        alt_prob = alt.get('probability', 0)
                        if alt_prob > 0.05:
                            alternatives.append({
                                'name': alt.get('name', 'Unknown'),
                                'confidence': round(alt_prob * 100, 1)
                            })
                    
                    return {
                        "status": "success",
                        "disease_name": disease_name,
                        "confidence": round(probability * 100, 1),
                        "description": description_en,
                        "description_hi": description_hi,
                        "common_names": common_names if isinstance(common_names, list) else [],
                        "treatments": treatments,
                        "treatment_combined": treatment_combined,
                        "severity": severity if severity else "Unknown",
                        "similar_images": similar_img_urls,
                        "alternatives": alternatives,
                        "external_url": ext_url if ext_url else ""
                    }
                
                # No suggestions found - likely healthy
                return {
                    "status": "success",
                    "disease_name": "Healthy",
                    "confidence": 100.0,
                    "description": "Your crop appears to be healthy. No diseases were detected.",
                    "description_hi": "आपकी फसल स्वस्थ दिखाई देती है। कोई बीमारी नहीं पाई गई।",
                    "common_names": [],
                    "treatments": {"biological": [], "chemical": [], "prevention": []},
                    "treatment_combined": "No treatment needed. Continue regular crop care practices.",
                    "severity": "None",
                    "similar_images": [],
                    "alternatives": [],
                    "external_url": ""
                }
            else:
                return {
                    "status": "success",
                    "disease_name": "Healthy",
                    "confidence": 100.0,
                    "description": "Your crop appears to be healthy or the disease is not recognized.",
                    "description_hi": "आपकी फसल स्वस्थ दिखाई देती है या रोग पहचाना नहीं गया।",
                    "common_names": [],
                    "treatments": {"biological": [], "chemical": [], "prevention": []},
                    "treatment_combined": "No treatment needed.",
                    "severity": "None",
                    "similar_images": [],
                    "alternatives": [],
                    "external_url": ""
                }
        else:
            return {
                "status": "error",
                "error_type": "API Error",
                "message": f"Failed to reach disease detection service. Status: {res.status_code}",
                "message_hi": f"रोग पहचान सेवा से संपर्क नहीं हो सका। स्थिति: {res.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "System Error",
            "message": f"An error occurred: {str(e)}",
            "message_hi": f"एक त्रुटि हुई: {str(e)}"
        }
