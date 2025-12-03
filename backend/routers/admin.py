from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
import os

router = APIRouter()

# Admin password from environment variable or default
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def admin_login(request: LoginRequest, response: Response):
    """Admin login endpoint"""
    if request.password == ADMIN_PASSWORD:
        # Set a simple cookie for authentication
        response.set_cookie(
            key="admin_session",
            value="authenticated",
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax"
        )
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.post("/logout")
async def admin_logout(response: Response):
    """Admin logout endpoint"""
    response.delete_cookie("admin_session")
    return {"success": True, "message": "Logged out successfully"}

@router.get("/check")
async def check_auth(request: Request):
    """Check if admin is authenticated"""
    admin_session = request.cookies.get("admin_session")
    
    if admin_session == "authenticated":
        return {"authenticated": True}
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")