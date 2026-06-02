from services.api_service import fetch_weather_data
from services.market_service import get_market_prices
from models.market_model import MarketModel

def get_weather_data(location):
    return fetch_weather_data(location)

def get_market_data(location):
    return get_market_prices(location)

def add_marketplace_listing(crop_name, quantity, price, image_path, is_eco=False):
    return MarketModel.create_listing(crop_name, quantity, price, image_path, is_eco)

def get_marketplace_listings():
    return MarketModel.get_all_listings()

