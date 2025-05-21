from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials

import requests

# Your Square Access Token
SQUARE_ACCESS_TOKEN = "EAAAlhJMyWPaslffhdKWs03uHpUkmzR3geyBCzIqNFIP6lKeAhAbtz0PHrnZyaBV"
SQUARE_API_BASE = "https://connect.squareup.com/v2"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Square-Version": "2025-04-16"
}

app = Flask(__name__)

# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
import os
import json
import base64

# Decode the service account from the env variable
creds_json = base64.b64decode(os.environ['GOOGLE_CREDS_B64']).decode()
creds_dict = json.loads(creds_json)

# Now authorize with in-memory credentials
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

client = gspread.authorize(creds)
sheet = client.open("Burger Counter").sheet1

@app.route('/webhook', methods=['POST'])
def square_webhook():
    data = request.get_json()
    
    try:
        order = data.get("data", {}).get("object", {}).get("order", {})
        items = order.get("line_items", [])
        burger_count = 0

        for item in items:
            if "burger" in item.get("name", "").lower():
                burger_count += int(item.get("quantity", 0))

        if burger_count > 0:
            current = int(sheet.acell("A2").value)
            sheet.update("A2", current + burger_count)

        return "OK", 200
    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

@app.route('/', methods=['GET'])
def home():
    return "Webhook is running!", 200

app.run(host='0.0.0.0', port=8080)
