Price Change Monitoring System

Overview

This project is designed to monitor price changes for products, keeping an eye on cost updates and stock levels. It works by pulling data from two API endpoints and scraping additional product details from a supplier’s website. Whenever a price drop is detected, the system sends a notification to a Discord channel, keeping you up to date on changes to the products you're tracking.

Features

Price Change Monitoring: Automatically checks for price drops by comparing the current price with the last known price pulled from the supplier’s API.
Web Scraping: Gathers extra product details like name, brand, UPC, and stock information from the supplier’s website to complement the data from the APIs.
Discord Notifications: Sends notifications to a Discord channel when a price drop is detected, including all relevant product details like SKU, price, brand, category, and more.
Stock Level Monitoring: Retrieves real-time stock levels from an API to include stock information in the price drop notifications.
How It Works

1. API Endpoints
The system uses two key API endpoints to gather product information:

a. Cost Changes Endpoint

Method: GET
What It Does: This endpoint returns information about price changes for products. It compares the current price with the last known price and provides details like SKU, current cost, and retail price.
Parameters:
memberNumber: The unique identifier for the requester.
changesSince: The date from which cost changes are needed.
Response: A list of products with details like SKU, the updated cost, and suggested retail prices.

b. Stock Level Endpoint

Method: GET
What It Does: This API gives the stock level of a product based on its SKU. This helps to provide a complete picture when a price drop occurs, including how many units are left in stock.
Parameters:
sku: The SKU of the product you want to check the stock for.
Response: Information about the product’s stock, such as the available quantity.
2. Web Scraping for Product Details
Whenever a product experiences a price drop, the system grabs extra details directly from the supplier’s website. The data collected includes:

Product Name
UPC
Brand
Category
Model Number
Product Image
This scraping is done using the BeautifulSoup library, which parses the HTML of the product page to extract the necessary details.

3. Discord Notifications
When a price change is detected, the system sends a detailed notification to a Discord channel using the Discord Webhook API. The notification includes:

Product Name
Product Image
Brand
Category
UPC
Current Price
Retail Price
Discount Percentage
Stock Level
Links to Amazon, Walmart, and Google search results for the product
The message is formatted nicely with embedded content, making it easy to read and interact with directly in Discord.

How It Works

Initialization: The system starts by loading sensitive data like API keys and webhook URLs from the .env file.

Check for Price Changes: The system checks for product price changes by querying the Cost Changes API.

Scrape Product Details: For each product that has a price change, the system scrapes additional details like name, UPC, brand, and stock info from the supplier’s website.

Check Stock Levels: The system retrieves the current stock level for each product using the Stock Level API.

Send Discord Notification: If a price drop is detected, the system sends a notification to the Discord channel, including all relevant product information.


## Webhook Preview


This is what the webhook notification looks like in Discord:

![Webhook Preview](https://github.com/user-attachments/assets/90cef7ff-f761-4cbd-ba74-39baa22fef1e)


