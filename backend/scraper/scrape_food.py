import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

FOOD_URL = "https://zuscoffee.com/category/food/page/{page}/"

def scrape_food():
    all_food_items = []
    page = 1

    while True:
        print(f"Scraping: {FOOD_URL.format(page=page)}")

        response = requests.get(FOOD_URL.format(page=page))
        
        # Stop if page doesn't exist (404)
        if response.status_code == 404:
            print("No more food pages found. Stopping.")
            break
            
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Each food item card
        food_item_cards = soup.select(".ecs-posts article.elementor-post")

        if not food_item_cards:
            print("No more food pages found. Stopping.")
            break

        for card in food_item_cards:
            # Title
            title_tag = card.select_one(".pt .elementor-heading-title")
            title = title_tag.get_text(strip=True) if title_tag else None

            # Category from article class list, e.g. category-food, category-pastries
            category = None
            article_classes = card.get("class", [])
            for cls in article_classes:
                if cls.startswith("category-"):
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

            all_food_items.append({
                "name": title,
                "category": category,
                "price": price,
                "image_url": image_url
            })

        page += 1

    os.makedirs("backend/data", exist_ok=True)

    with open("backend/data/food.json", "w", encoding="utf-8") as f:
        json.dump(all_food_items, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(all_food_items)
    df.to_csv("backend/data/food.csv", index=False)

    print(f"Scraped total {len(all_food_items)} food items!")

if __name__ == "__main__":
    scrape_food()
