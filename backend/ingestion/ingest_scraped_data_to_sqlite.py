import os
import json
import sqlite3
import re

# -------------------- Config --------------------
DATA_DIR = "backend/data"
DATABASE_DIR = "backend/database"

# JSON data files
DRINKWARE_JSON = os.path.join(DATA_DIR, "drinkware.json")
OUTLETS_JSON = os.path.join(DATA_DIR, "outlets.json")
# You can add FOOD_JSON, DRINKS_JSON etc. similarly

# Database file
DATABASE_PATH = os.path.join(DATABASE_DIR, "zus_coffee_internal.db")

# -------------------- Helper Functions --------------------
def create_database():
    """Creates database and tables if they don't exist."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Outlets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outlets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        address TEXT,
        maps_url TEXT
    )
    """)

    # Drinkware / products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drinkware (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        link TEXT,
        category TEXT,
        price REAL,
        image_url TEXT
    )
    """)

    # Add more tables if needed (e.g., food, drinks)

    conn.commit()
    conn.close()
    print("Database and tables are ready!")

def load_json(file_path):
    """Load JSON data from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_price(price_str):
    """Extract numeric price from a string like 'Sale priceRM79.00'."""
    if not price_str:
        return 0.0
    match = re.search(r"(\d+(\.\d+)?)", price_str)
    return float(match.group(1)) if match else 0.0

def ingest_drinkware(data):
    """Ingest drinkware/products data into SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for item in data:
        cursor.execute("""
        INSERT INTO drinkware (name, link, category, price, image_url)
        VALUES (?, ?, ?, ?, ?)
        """, (
            item.get("name"),
            item.get("link"),
            item.get("category"),
            parse_price(item.get("price")),
            item.get("image_url")
        ))
    conn.commit()
    conn.close()
    print(f"Ingested {len(data)} drinkware items.")

def ingest_outlets(data):
    """Ingest outlets data into SQLite."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    for outlet in data:
        cursor.execute("""
        INSERT INTO outlets (name, category, address, maps_url)
        VALUES (?, ?, ?, ?)
        """, (
            outlet.get("name"),
            outlet.get("category"),
            outlet.get("address"),
            outlet.get("maps_url")
        ))
    conn.commit()
    conn.close()
    print(f"Ingested {len(data)} outlets.")

# -------------------- Main Script --------------------
if __name__ == "__main__":
    create_database()

    # Load JSON files
    outlets_data = load_json(OUTLETS_JSON)
    drinkware_data = load_json(DRINKWARE_JSON)

    # Ingest into SQLite
    ingest_outlets(outlets_data)
    ingest_drinkware(drinkware_data)

    print("All data ingested successfully!")
