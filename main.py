from flask import Flask, request
import os
import json
import base64
import gspread
import requests
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# --- Square API Setup ---
SQUARE_ACCESS_TOKEN = "EAAAlhJMyWPaslffhdKWs03uHpUkmzR3geyBCzIqNFIP6lKeAhAbtz0PHrnZyaBV"
BURGER_CATEGORY_ID = "UNPZDJDG35325CJW6E6ZZAAU"
SQUARE_API_BASE = "https://connect.squareup.com/v2"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Square-Version": "2025-04-16"
}

# --- Google Sheets Setup ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from environment variable (base64-encoded JSON)
creds_json = base64.b64decode(os.environ["GOOGLE_CREDS_B64"]).decode()
creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# Connect to Google Sheet
gc = gspread.authorize(creds)
SHEET_ID = "1fjbrsudBew-6XcYL9b7wdj7WliSPniTjOTFKeFcnMB8"  # Use open_by_key to avoid needing Drive API
sheet = gc.open_by_key(SHEET_ID).sheet1


# --- Helper: Get Category ID for a Catalog Item ---
def get_category_id_for_item(item_id):
    url = f"{SQUARE_API_BASE}/catalog/object/{item_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        obj = response.json().get("object", {})
        item_data = obj.get("item_data", {})
        return item_data.get("category_id")
    else:
        print(f"Failed to fetch catalog item {item_id}: {response.status_code}")
        return None


# --- Webhook Endpoint ---
@app.route("/webhook", methods=["POST"])
def square_webhook():
    data = request.get_json()
    print("Webhook received:", json.dumps(data, indent=2))

    try:
        order = data.get("data", {}).get("object", {}).get("order", {})
        items = order.get("line_items", [])

        burger_count = 0

        for item in items:
            quantity = int(item.get("quantity", 0))
            item_id = item.get("catalog_object_id")

            if item_id:
                category_id = get_category_id_for_item(item_id)
                if category_id == BURGER_CATEGORY_ID:
                    burger_count += quantity

        if burger_count > 0:
            current = int(sheet.acell("A2").value)
            sheet.update("A2", current + burger_count)
                        print(f"Updated counter: +{burger_count} → total: {current + burger_count}")
                    else:
                        print("No burger items found in order.")
            
                    return "OK", 200
            
                except Exception as e:
                    print(f"Error processing webhook: {e}")
                    return "Error", 500
            
            
# --- Basic Ping Endpoint ---
@app.route("/", methods=["GET"])
def home():
    return "Burger Counter Webhook is running!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
