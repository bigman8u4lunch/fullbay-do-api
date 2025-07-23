import os
import requests
import hashlib
from dotenv import load_dotenv
from datetime import date

load_dotenv()
KEY = os.getenv("FULLBAY_API_KEY")

def get_public_ip():
    return requests.get("https://api.ipify.org").text

def generate_token(key, today, ip):
    raw = f"{key}{today}{ip}"
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()

def fetch_fullbay_data(endpoint_url, start, end):
    ip = get_public_ip()
    today = date.today().strftime("%Y-%m-%d")
    token = generate_token(KEY, today, ip)
    
    params = {
        "key": KEY,
        "token": token,
        "startDate": start,
        "endDate": end
    }
    
    response = requests.get(endpoint_url, params=params)
    response.raise_for_status()
    return response.json()
