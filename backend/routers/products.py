import sqlite3
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import os

from schemas import Product, ProductCreate, ProductUpdate

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

@router.get("/", response_model=List[Product])
def get_all_products(skip: int = 0, limit: int = 100):
    """
    Get all products with pagination.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drinkware LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        products = [dict(row) for row in rows]
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    """
    Get a specific product by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drinkware WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product: {str(e)}")

@router.post("/", response_model=Product, status_code=201)
def create_product(product: ProductCreate):
    """
    Create a new product.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO drinkware (name, link, category, price, image_url)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product.name, product.link, product.category, product.price, product.image_url)
        )
        conn.commit()
        product_id = cursor.lastrowid
        
        # Fetch the created product
        cursor.execute("SELECT * FROM drinkware WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductUpdate):
    """
    Update an existing product.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT * FROM drinkware WHERE id = ?", (product_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        if product.name is not None:
            update_fields.append("name = ?")
            values.append(product.name)
        if product.link is not None:
            update_fields.append("link = ?")
            values.append(product.link)
        if product.category is not None:
            update_fields.append("category = ?")
            values.append(product.category)
        if product.price is not None:
            update_fields.append("price = ?")
            values.append(product.price)
        if product.image_url is not None:
            update_fields.append("image_url = ?")
            values.append(product.image_url)
        
        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(product_id)
        query = f"UPDATE drinkware SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Fetch updated product
        cursor.execute("SELECT * FROM drinkware WHERE id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    """
    Delete a product.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT * FROM drinkware WHERE id = ?", (product_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Product not found")
        
        cursor.execute("DELETE FROM drinkware WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")

@router.get("/search/", response_model=List[Product])
def search_products(
    name: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 100
):
    """
    Search products with various filters.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM drinkware WHERE 1=1"
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
        raise HTTPException(status_code=500, detail=f"Error searching products: {str(e)}")
