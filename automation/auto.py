import json
import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client, Client, ClientOptions
from datetime import datetime, timezone
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
print(r)
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SECRET_KEY")
supabase: Client = create_client(url,key)
gundamplanet_url = "https://www.gundamplanet.com/collections/gunpla/products.json"

'''
To create time stamp in utc to plug into supabase
Also use this 
now = datetime.now(timezone.utc).isoformat()

If there is no items in redis chache, then add items 


'''



def fetch_all_price_history(table_name="Items"):
    all_data = []
    page_size = 1000  # Supabase's standard batch limit
    current_page = 0 
    while True:
        # Calculate range
        start_from = current_page * page_size
        end_at = start_from + page_size - 1

        # Fetch batch
        response = supabase.table(table_name).select("*").range(start_from, end_at).execute()
        batch_data = response.data

        if not batch_data:
            break  # No more data left in the table

        all_data.extend(batch_data)
        current_page += 1

    return all_data

def main():
    # items_data = fetch_all_price_history()
    # print(items_data)
    results = []
    history = {}
    page = 1
    exit(1)
    while True:
        print(f"[gundamplanet] Checking page {page}")
        params = {"limit": 250, "page": page, "sort_by": "created-descending"}
        response = requests.get(gundamplanet_url, params=params, timeout=30)
        response.raise_for_status()
        products = response.json().get("products", [])
        if not products:
            print("[gundamplanet] No more products")
            break
        for product in products:
            title = product.get("title", "")
            variants = product.get("variants", [])
            handle = product.get("handle")
            url = "https://www.gundamplanet.com/products/" + handle
            if not variants:
                continue
            variant = variants[0]
            available = variant.get("available") # bool
            price = float(variant["price"]) # current price
            compare_at = variant.get("compare_at_price") # msrp if on sale
            results.append({
                "item_name": title,
                "current_price": price,
                "seller": "GundamPlanet",
                "in_stock": available,
                "url": url,
                "msrp": compare_at if compare_at else price
            })
            history_id = f'gundamplanet::{title}'
            history[history_id] = {"price": price}
        # page+=1
        break
        time.sleep(1)
        
    print(history)


if __name__ == "__main__":
    main()