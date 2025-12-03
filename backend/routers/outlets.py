import sqlite3
from fastapi import APIRouter, HTTPException
from typing import Optional, List
import os

from schemas import Outlet, OutletCreate, OutletUpdate

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

@router.get("/", response_model=List[Outlet])
def get_all_outlets(skip: int = 0, limit: int = 100):
    """
    Get all outlets with pagination.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outlets LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        conn.close()
        
        outlets = [dict(row) for row in rows]
        return outlets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching outlets: {str(e)}")

@router.get("/{outlet_id}", response_model=Outlet)
def get_outlet(outlet_id: int):
    """
    Get a specific outlet by ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Outlet not found")
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching outlet: {str(e)}")

@router.post("/", response_model=Outlet, status_code=201)
def create_outlet(outlet: OutletCreate):
    """
    Create a new outlet.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO outlets (name, category, address, maps_url)
            VALUES (?, ?, ?, ?)
            """,
            (outlet.name, outlet.category, outlet.address, outlet.maps_url)
        )
        conn.commit()
        outlet_id = cursor.lastrowid
        
        # Fetch the created outlet
        cursor.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating outlet: {str(e)}")

@router.put("/{outlet_id}", response_model=Outlet)
def update_outlet(outlet_id: int, outlet: OutletUpdate):
    """
    Update an existing outlet.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if outlet exists
        cursor.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Outlet not found")
        
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        if outlet.name is not None:
            update_fields.append("name = ?")
            values.append(outlet.name)
        if outlet.category is not None:
            update_fields.append("category = ?")
            values.append(outlet.category)
        if outlet.address is not None:
            update_fields.append("address = ?")
            values.append(outlet.address)
        if outlet.maps_url is not None:
            update_fields.append("maps_url = ?")
            values.append(outlet.maps_url)
        
        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(outlet_id)
        query = f"UPDATE outlets SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        # Fetch updated outlet
        cursor.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating outlet: {str(e)}")

@router.delete("/{outlet_id}", status_code=204)
def delete_outlet(outlet_id: int):
    """
    Delete an outlet.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if outlet exists
        cursor.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        existing = cursor.fetchone()
        if existing is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Outlet not found")
        
        cursor.execute("DELETE FROM outlets WHERE id = ?", (outlet_id,))
        conn.commit()
        conn.close()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting outlet: {str(e)}")

@router.get("/search/", response_model=List[Outlet])
def search_outlets(
    name: Optional[str] = None,
    category: Optional[str] = None,
    address: Optional[str] = None,
    limit: int = 100
):
    """
    Search outlets with various filters.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM outlets WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        
        if category:
            query += " AND category LIKE ?"
            params.append(f"%{category}%")
        
        if address:
            query += " AND address LIKE ?"
            params.append(f"%{address}%")
        
        query += " LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching outlets: {str(e)}")
