import requests
from datetime import datetime, timezone
import os
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import quote
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch sensitive data from environment variables
memberNumber = '4951'
endpoint = os.getenv("ENDPOINT")
key = os.getenv("API_KEY")  
discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")  # Discord webhook URL from .env file
PRICE_HISTORY_FILE = "price_history.json"
LAST_CHECKED_FILE = "last_checked_time.json"
SUPPLIER_BASE_URL = os.getenv("SUPPLIER_BASE_URL")  # Supplier base URL from .env file
STOCK_API_URL = os.getenv("STOCK_API_URL")  # Stock API URL from .env file

# Cache notified items to prevent duplicate webhooks
notified_items = set()

# Get the last checked date from a file or return the current UTC time if not available
def get_last_checked_date():
    if os.path.exists(LAST_CHECKED_FILE):
        with open(LAST_CHECKED_FILE, "r") as file:
            last_checked_data = json.load(file)
            return last_checked_data.get("last_checked", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    return last_checked_data.get("last_checked", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

# Save the current UTC time as the last checked time
def save_last_checked_time():
    last_checked_data = {"last_checked": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")}
    with open(LAST_CHECKED_FILE, "w") as file:
        json.dump(last_checked_data, file)

# Fetch cost changes from the API
def fetch_cost_changes(last_checked_date):
    try:
        formatted_date = datetime.strptime(last_checked_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        formatted_date = datetime.strptime(last_checked_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    request_url = f"{endpoint}?changesSince={formatted_date}"
    headers = {"Ocp-Apim-Subscription-Key": key}
    params = {"memberNumber": memberNumber}
    response = requests.get(request_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
        
    elif response.status_code == 404:
        print(f"No changes found since {last_checked_date}")
        return []
    else:
        print(f"Failed to fetch data, Status Code: {response.status_code}, Response: {response.text}")
        response.raise_for_status()

# Load previous prices from file (if exists)
def load_previous_prices():
    if os.path.exists(PRICE_HISTORY_FILE):
        with open(PRICE_HISTORY_FILE, "r") as file:
            return json.load(file)
    return {}

# Save the current prices to file for future comparison
def save_current_prices(prices):
    with open(PRICE_HISTORY_FILE, "w") as file:
        json.dump(prices, file)

# Function to scrape product details from distributors website
def scrape_product_details(sku):
    product_url = f"{SUPPLIER_BASE_URL}/product/{sku}/"  # Directly use the product URL with SKU
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    try:
        response = requests.get(product_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch product details for SKU: {sku}, Status Code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape product name, image, UPC, brand, and category
        product_name = soup.select_one('span[role="name"].font-black').get_text(strip=True) if soup.select_one('span[role="name"].font-black') else "No name found"
        product_image = soup.select_one('.pdp__prodimage')['src'] if soup.select_one('.pdp__prodimage') else None
        upc = soup.select_one('span[role="upc"]').get_text(strip=True) if soup.select_one('span[role="upc"]') else "No UPC found"
        
        # Find brand in the specifications table
        brand_row = soup.find('td', text="Brand")  # Locate the row with "Brand"
        if brand_row:
            brand = brand_row.find_next('td').get_text(strip=True)  # Get the value in the next <td> element
        else:
            brand = "No brand found"
        
        # Try extracting category from the meta tags or structured data
        category_elements = soup.select('span[itemprop="name"].cmp-breadcrumb__name')
        category = category_elements[1].get_text(strip=True) if category_elements else "No category found"

        model = soup.find('span', {'role': 'modelNumber'}).get_text(strip=True) if soup.find('span', {'role': 'modelNumber'}) else "No model number found"

        return {
            "name": product_name,
            "image": product_image,
            "link": product_url,
            "upc": upc,
            "brand": brand,
            "category": category,
            "model": model
        }
    except Exception as e:
        print(f"Error scraping product details for SKU: {sku}: {e}")
        return None

#function to post to discord

def post_to_discord(item, current_cost, product_details, stock_level):
    if product_details is None:
        print(f"Skipping SKU {item.get('sku')} - Failed to retrieve product details")
        return
    
    product_name = product_details.get("name", "Unknown Product")
    encoded_product_name = quote(product_name)
    if item.get("sku") in notified_items:
        return

    try:
        # Ensure numerical values are properly formatted
        retail_price = item.get("suggestedRetailPrice", 0) or 0  # Default to 0 if None
        discount_percent = (
            ((retail_price - current_cost) / retail_price * 100) if retail_price > 0 else 0
        )

        # Filter out fields that are None or empty
        fields = []

        if product_details.get("brand"):
            fields.append({"name": "Brand", "value": product_details["brand"]})
        if product_details.get("category"):
            fields.append({"name": "Category", "value": product_details["category"]})
        if item.get("sku"):
            fields.append({"name": "SKU", "value": item["sku"]})
        fields.append({"name": "Model Number", "value": product_details["model"]})
        if product_details.get("upc"):
            fields.append({"name": "UPC", "value": product_details["upc"]})
        if retail_price:
            fields.append({"name": "Current Price", "value": f"${current_cost:.2f}", "inline": True})
        fields.append({"name": "Retail Price", "value": f"${retail_price:.2f}", "inline": True})
        fields.append({"name": "Discount %", "value": f"{round(discount_percent, 1):.1f}%", "inline": True})
        
        fields.append({"name": "Total Stock", "value": str(stock_level), "inline": True})  # Display total stock level
        
        fields.append({"name": "Links", "value": f"[Amazon](https://www.amazon.com/s?k={encoded_product_name}) - "
              f"[Walmart](https://www.walmart.com/search/?query={encoded_product_name}) - "
              f"[Google](https://www.google.com/search?q={encoded_product_name})",
    "inline": False
})


        # Validate image URL
        thumbnail = None
        if product_details.get("image") and product_details["image"].startswith("http"):
            thumbnail = {"url": product_details["image"]}
        
        est = pytz.timezone("America/New_York")
        current_time = datetime.now(est).strftime("%B %d at %I:%M %p")

        payload = {
            "embeds": [{
                "title": f"Price Alert! 🛒 Price drop for {product_name}",
                "description": f"The price for **{product_name}** has decreased.",
                "url": product_details.get("link"),
                "timestamp": current_time,
                "thumbnail": thumbnail,
                "fields": fields
            }]
        }
        response = requests.post(discord_webhook_url, json=payload)

        if response.status_code == 204:
            print(f"Webhook successfully sent for {product_name}")
            notified_items.add(item.get("sku"))  # Mark this SKU as notified
        else:
            print(f"Failed to send webhook for {product_name}, Status Code: {response.status_code}")

    except Exception as e:
        print(f"Error posting to Discord for {item.get('sku')}: {e}")

def check_for_price_changes():
    last_checked_date = get_last_checked_date()
    cost_changes = fetch_cost_changes(last_checked_date)

    if cost_changes:
        previous_prices = load_previous_prices()
        new_prices = {}

        for item in cost_changes:
            sku = item.get("sku")
            current_cost = item.get("currentCost")
            if sku and current_cost is not None:
                if sku in previous_prices and previous_prices[sku] != current_cost:
                    product_details = scrape_product_details(sku)
                    stock_level_response = requests.get(STOCK_API_URL + sku)
                    stock_data = stock_level_response.json() if stock_level_response.status_code == 200 else None
                    stock_level = stock_data.get('stock', 'N/A') if stock_data else 'N/A'

                    post_to_discord(item, current_cost, product_details, stock_level)

                new_prices[sku] = current_cost
        
        save_current_prices(new_prices)
        save_last_checked_time()

if __name__ == "__main__":
    check_for_price_changes()

