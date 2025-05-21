from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
import base64
import os

creds_json = base64.b64decode(os.environ['GOOGLE_CREDS_B64']).decode()
creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
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
