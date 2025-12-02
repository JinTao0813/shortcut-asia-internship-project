import json
import os
import sqlite3

DATA_DIR = "backend/data"
JSON_PATH = os.path.join(DATA_DIR, "outlets.json")
DB_PATH = os.path.join(DATA_DIR, "outlets.db")

os.makedirs(DATA_DIR, exist_ok=True)

def create_db_and_insert():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        outlets = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS outlets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        address TEXT,
        maps_url TEXT
    );
    """)
    conn.commit()

    cur.executemany("""
        INSERT INTO outlets (name, category, address, maps_url) VALUES (?, ?, ?, ?)
    """, [(o.get("name"), o.get("category"), o.get("address"), o.get("maps_url")) for o in outlets])

    conn.commit()
    conn.close()
    print(f"Inserted {len(outlets)} outlets into {DB_PATH}")

if __name__ == "__main__":
    create_db_and_insert()
