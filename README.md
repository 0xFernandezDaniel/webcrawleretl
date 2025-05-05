Price Change Monitoring System

Overview

This project monitors price changes for products by fetching data from two API endpoints and performing web scraping to gather additional product details. The system sends notifications to a Discord channel whenever a price drop is detected. The solution is designed for monitoring supplier products with SKU-based pricing, stock levels, and other product information.

Features

Price Change Monitoring: Fetches product cost changes from a supplier's API and compares it with the previous price to detect drops.
Web Scraping: Scrapes product details such as name, brand, UPC, and stock information from the supplier’s website.
Discord Notifications: Sends detailed price change notifications to a Discord channel with product information, including SKU, price, brand, category, and more.
Stock Level Monitoring: Retrieves stock levels from an API endpoint and includes this information in the notifications.
Components

1. API Endpoints
Two main API endpoints are used to gather product information:

a. Cost Changes API

Endpoint: https://api.doitbestdataxchange.com/cost/itemcostchanges
Method: GET
Description: This endpoint provides the cost changes for products. The system checks for changes in the product cost since the last time the system was run. It returns the SKU, cost details, and other pricing-related information.
Parameters:
memberNumber: Unique identifier for the member requesting the data.
changesSince: The date since when the cost changes are requested.
Response: A list of product items with details like SKU, current cost, suggested retail price, and more.
b. Stock Level API

Endpoint: https://api.doitbestdataxchange.com/InventoryBySKU/inventory?sku=
Method: GET
Description: This API provides information about the stock levels of products based on their SKU. The system uses this data to include stock information in the price drop notifications.
Parameters:
sku: The SKU of the product to retrieve stock levels.
Response: Stock information, including the available quantity of the product.
2. Web Scraping for Product Details
For each product that has experienced a price change, the system scrapes additional details directly from the supplier’s website:

Scraped Information:
Product Name: The name of the product.
UPC: Universal Product Code (UPC) associated with the product.
Brand: The product’s brand.
Category: The product's category.
Model Number: The model number associated with the product.
Product Image: The URL of the product’s image.
The scraping is done using the BeautifulSoup library, which parses the HTML of the supplier’s product page and extracts the necessary details.

3. Discord Notifications
Once a price change is detected, the system sends a message to a Discord channel using the Discord Webhook API. The message includes:

Product Name
Product Image
Brand
Category
UPC
Current Price
Retail Price
Discount Percentage
Stock Level
Product Links to Amazon, Walmart, and Google search results for the product.
The webhook message is structured in an embedded format, making it easy to read and interact with on Discord.

How It Works

Initialization: The system loads environment variables from the .env file for API keys, webhook URLs, and other sensitive data.
Check for Price Changes: The system fetches product cost changes since the last run using the Cost Changes API endpoint.
Scrape Product Details: For each product that has a price change, the system scrapes additional product details from the supplier’s website using web scraping techniques (BeautifulSoup).
Check Stock Levels: The system retrieves stock levels for each product from the Stock Level API.
Send Discord Notification: If a price change is detected, a message is sent to a Discord channel with all relevant product information, including price, stock, and product details.

## Webhook Preview


This is what the webhook notification looks like in Discord:

![Webhook Preview](https://github.com/user-attachments/assets/90cef7ff-f761-4cbd-ba74-39baa22fef1e)


