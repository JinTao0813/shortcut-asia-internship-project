import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

DRINKS_URL = "https://zuscoffee.com/category/drinks/page/{page}/"

def scrape_drinks():
    all_drinks = []
    page = 1

    while True:
        print(f"Scraping: {DRINKS_URL.format(page=page)}")

        response = requests.get(DRINKS_URL.format(page=page))
        
        # Stop if page doesn't exist (404)
        if response.status_code == 404:
            print("No more drinks pages found. Stopping.")
            break
            
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Each drink item card
        drink_cards = soup.select(".ecs-posts article.elementor-post")

        if not drink_cards:
            print("No more drinks pages found. Stopping.")
            break

        for card in drink_cards:
            # Title
            title_tag = card.select_one(".pt .elementor-heading-title")
            title = title_tag.get_text(strip=True) if title_tag else None

            # Category from article class list, e.g. category-drinks, category-frappe-buddy
            category = None
            article_classes = card.get("class", [])
            for cls in article_classes:
                if cls.startswith("category-") and cls != "category-drinks":
                    category = cls.replace("category-", "")
                    break

            # No price shown on listing page
            price = None

            # Image
            img_tag = card.select_one(".modal-link a img")
            image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

            if not title or not image_url:
                continue

            all_drinks.append({
                "name": title,
                "category": category,
                "price": price,
                "image_url": image_url
            })

        page += 1

    os.makedirs("backend/data", exist_ok=True)

    with open("backend/data/drinks.json", "w", encoding="utf-8") as f:
        json.dump(all_drinks, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(all_drinks)
    df.to_csv("backend/data/drinks.csv", index=False)

    print(f"Scraped total {len(all_drinks)} drinks!")

if __name__ == "__main__":
    scrape_drinks()
