import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import hashlib
from pymongo.server_api import ServerApi
from config import Config


client = MongoClient("mongodb://mongo:27017/", server_api=ServerApi('1'))
db = client["scraper_db"]

class EbayScraper:
    def __init__(self):
        self.base_url = "https://www.ebay.com/sch/i.html"
        self.client = client
        self.db = db

    def _convert_price_to_number(self, price):
        try:
            return float(price.replace('$', '').replace(',', ''))
        except ValueError:
            return None

    def _extract_price(self, price_str):
        prices = price_str.split(' to ')
        if len(prices) == 1:
            return self._convert_price_to_number(prices[0])
        return None

    def generate_id(self, title, link):
        return hashlib.md5(f"{title}{link}".encode()).hexdigest()

    def scrape(self, query, min_price, max_price, sort_order, free_shipping, exclude_price_range):
        params = {
            "_nkw": query,
            "_udlo": min_price,
            "_udhi": max_price,
            "_sop": 10 if sort_order == 'asc' else 16,
            "LH_FS": "1" if free_shipping else None,
        }
        response = requests.get(self.base_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        collection = self.db[query]

        for item in soup.select(".s-item"):
            title = item.select_one(".s-item__title")
            price = item.select_one(".s-item__price")
            link = item.select_one(".s-item__link")["href"]
            shipping = item.select_one(".s-item__shipping")
            location = item.select_one(".s-item__location")
            price_value = self._extract_price(price.text) if price else None
            if title and price and link and price_value is not None:
                if exclude_price_range and " to " in price.text:
                    continue
                if title.text.strip().lower() == "shop on ebay" and price_value == 20.0:
                    continue

                item_id = self.generate_id(title.text.strip(), link)
                item_data = {
                    "_id": item_id,
                    "title": title.text.strip(),
                    "price": price.text.strip(),
                    "price_value": price_value,
                    "shipping": shipping.text.strip() if shipping else "Free International Shipping",
                    "location": location.text.strip() if location else "Unknown",
                    "link": link
                }
                items.append(item_data)

                # Użycie update_one z upsert=True
                try:
                    collection.update_one({"_id": item_id}, {"$set": item_data}, upsert=True)
                except Exception as e:
                    print(f"Error saving to DB: {e}")

        items = sorted(items, key=lambda x: x['price_value'], reverse=(sort_order == 'desc'))
        return items