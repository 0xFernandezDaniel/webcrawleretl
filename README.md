# Item Price Monitor

This script monitors item cost changes from a MRO distributors API and sends price drop alerts with product info to a Discord channel using a webhook.

## Features
- Tracks SKU price changes over time
- Scrapes product metadata (brand, UPC, image, etc.) from the distributors website, since it is not provided through the API.
- Sends formatted Discord alerts with product info
- Caches results to avoid duplicate alerts


## 📸 Webhook Preview

This is what the webhook notification looks like in Discord:

![Webhook Preview](![oZlnWgn - Imgur](https://github.com/user-attachments/assets/90cef7ff-f761-4cbd-ba74-39baa22fef1e)
)


