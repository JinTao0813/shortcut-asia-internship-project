import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

OUTLETS_URL = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/page/{page}/"


def scrape_outlets():

    all_outlets = [] 
    page = 1

    while True:
        print(f"Scraping: {OUTLETS_URL.format(page=page)}")

        response = requests.get(OUTLETS_URL.format(page=page))
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        outlet_cards = soup.select("article.elementor-post.elementor-grid-item")

        if not outlet_cards:
            print("No more outlet pages found. Stopping.")
            break

        for card in outlet_cards:

            title_tag = card.select_one("p.elementor-heading-title")
            title = title_tag.get_text(strip=True) if title_tag else None

            category_tag = card.select_one("h2.elementor-heading-title a")
            category = category_tag.get_text(strip=True) if category_tag else None

            address_tag = card.select_one(".elementor-widget-theme-post-content p")
            address = address_tag.get_text(strip=True) if address_tag else None

            direction_tag = card.select_one("a.premium-button")
            maps_url = direction_tag["href"] if direction_tag else None

            if not title or not address or not maps_url or not category:
                continue

            all_outlets.append({
                "name": title,
                "category": category,
                "address": address,
                "maps_url": maps_url
            })

        page += 1

    os.makedirs("backend/data", exist_ok=True)

    with open("backend/data/outlets.json", "w", encoding="utf-8") as f:
        json.dump(all_outlets, f, indent=4, ensure_ascii=False)

    pd.DataFrame(all_outlets).to_csv("backend/data/outlets.csv", index=False)

    print(f"Scraped total {len(all_outlets)} outlets successfully!")

if __name__ == "__main__":
    scrape_outlets()
