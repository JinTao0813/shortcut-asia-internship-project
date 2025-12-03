import sqlite3
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import os

from schemas import Drink, DrinkCreate, DrinkUpdate

router = APIRouter()

# Database path
DB_PATH = os.path.join("database", "zus_coffee_internal.db")

# ==================== Helper Functions ====================
def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== Endpoints ====================

@router.get("/", response_model=List[Drink])
def get_all_drinks(skip: int = 0, limit: int = 100):
    """
    Get all drinks with pagination.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drinks LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        drinks = [dict(row) for row in rows]
        return drinks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drinks: {str(e)}")

@router.get("/{drink_id}", response_model=Drink)
def get_drink(drink_id: int):
    """
    Get a specific drink by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Drink not found")
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drink: {str(e)}")

@router.post("/", response_model=Drink, status_code=201)
def create_drink(drink: DrinkCreate):
    """
    Create a new drink.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO drinks (name, category, price, image_url)
            VALUES (?, ?, ?, ?)
            """,
            (drink.name, drink.category, drink.price, drink.image_url)
        )
        conn.commit()
        drink_id = cursor.lastrowid
        
        # Fetch the created drink
        cursor.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating drink: {str(e)}")

@router.put("/{drink_id}", response_model=Drink)
def update_drink(drink_id: int, drink: DrinkUpdate):
    """
    Update an existing drink.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if drink exists
        cursor.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Drink not found")
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        if drink.name is not None:
            update_fields.append("name = ?")
            values.append(drink.name)
        if drink.category is not None:
            update_fields.append("category = ?")
            values.append(drink.category)
        if drink.price is not None:
            update_fields.append("price = ?")
            values.append(drink.price)
        if drink.image_url is not None:
            update_fields.append("image_url = ?")
            values.append(drink.image_url)
        
        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(drink_id)
        query = f"UPDATE drinks SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Fetch updated drink
        cursor.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating drink: {str(e)}")

@router.delete("/{drink_id}", status_code=204)
def delete_drink(drink_id: int):
    """
    Delete a drink.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if drink exists
        cursor.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Drink not found")
        
        cursor.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))
        conn.commit()
        conn.close()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting drink: {str(e)}")

@router.get("/search/", response_model=List[Drink])
def search_drinks(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 100
):
    """
    Search drinks with various filters.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM drinks WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching drinks: {str(e)}")
