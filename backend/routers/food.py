import sqlite3
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import os

from schemas import Food, FoodCreate, FoodUpdate

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

@router.get("/", response_model=List[Food])
def get_all_food(skip: int = 0, limit: int = 100):
    """
    Get all food items with pagination.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        food_items = [dict(row) for row in rows]
        return food_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching food items: {str(e)}")

@router.get("/{food_id}", response_model=Food)
def get_food(food_id: int):
    """
    Get a specific food item by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM food WHERE id = ?", (food_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Food item not found")
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching food item: {str(e)}")

@router.post("/", response_model=Food, status_code=201)
def create_food(food: FoodCreate):
    """
    Create a new food item.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO food (name, category, price, image_url)
            VALUES (?, ?, ?, ?)
            """,
            (food.name, food.category, food.price, food.image_url)
        )
        conn.commit()
        food_id = cursor.lastrowid
        
        # Fetch the created food item
        cursor.execute("SELECT * FROM food WHERE id = ?", (food_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating food item: {str(e)}")

@router.put("/{food_id}", response_model=Food)
def update_food(food_id: int, food: FoodUpdate):
    """
    Update an existing food item.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if food item exists
        cursor.execute("SELECT * FROM food WHERE id = ?", (food_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Food item not found")
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        if food.name is not None:
            update_fields.append("name = ?")
            values.append(food.name)
        if food.category is not None:
            update_fields.append("category = ?")
            values.append(food.category)
        if food.price is not None:
            update_fields.append("price = ?")
            values.append(food.price)
        if food.image_url is not None:
            update_fields.append("image_url = ?")
            values.append(food.image_url)
        
        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(food_id)
        query = f"UPDATE food SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Fetch updated food item
        cursor.execute("SELECT * FROM food WHERE id = ?", (food_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating food item: {str(e)}")

@router.delete("/{food_id}", status_code=204)
def delete_food(food_id: int):
    """
    Delete a food item.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if food item exists
        cursor.execute("SELECT * FROM food WHERE id = ?", (food_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Food item not found")
        
        cursor.execute("DELETE FROM food WHERE id = ?", (food_id,))
        conn.commit()
        conn.close()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting food item: {str(e)}")

@router.get("/search/", response_model=List[Food])
def search_food(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 100
):
    """
    Search food items with various filters.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM food WHERE 1=1"
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
        raise HTTPException(status_code=500, detail=f"Error searching food items: {str(e)}")
