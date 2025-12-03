import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

DRINKWARE_URL = "https://shop.zuscoffee.com/collections/drinkware"

def scrape_drinkware():
    response = requests.get(DRINKWARE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    product_cards = soup.select(".product-card")

    for card in product_cards:

        title_tag = card.select_one(".product-card__title a")
        title = title_tag.get_text(strip=True) if title_tag else None

        link = None
        if title_tag and title_tag.has_attr("href"):
            link = title_tag["href"]
            if link.startswith("/"):
                link = "https://shop.zuscoffee.com" + link

        category_tag = card.select_one(".product-card__category")
        category = category_tag.get_text(strip=True) if category_tag else None

        price_tag = card.select_one("sale-price")
        price = price_tag.get_text(strip=True) if price_tag else None

        img_tag = card.select_one(".product-card__figure a img")
        image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
        if image_url and image_url.startswith("//"):
            image_url = "https:" + image_url

        products.append({
            "name": title,
            "link": link,
            "category": category,
            "price": price,
            "image_url": image_url
        })

    os.makedirs("backend/data", exist_ok=True)

    with open("backend/data/drinkware.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(products)
    df.to_csv("backend/data/drinkware.csv", index=False)

    print(f"Scraped {len(products)} drinkware products.")

if __name__ == "__main__":
    scrape_drinkware()
