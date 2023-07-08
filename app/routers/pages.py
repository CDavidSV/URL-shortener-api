from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app import auth
from .. import database as db

import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
DB_NAME = os.getenv("DB_NAME")

@router.get("/", response_class=HTMLResponse)
async def root(request: Request, current_user: auth.User = Depends(auth.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/signup")
async def register(request: Request):
    return templates.TemplateResponse("sign-up.html", {"request": request})

@router.get("/{back_half_id}")
async def access_page(back_half_id: str, request: Request):
    short_url = db.execute_query("shorturls.db", "SELECT * FROM ShortURL WHERE ShortURLId = ?", (back_half_id,))
    if len(short_url) == 0:
        return templates.TemplateResponse("page_not_found.html", {"request": request})
    
    # Increment the number of times the short url has been accessed.
    db.execute_query(DB_NAME, "UPDATE ShortURL SET ViewCount = ? WHERE ShortURLId = ?", (short_url[0][4] + 1, back_half_id,), True)
    
    # Redirect to the original URL.
    return RedirectResponse(url=short_url[0][1], status_code=302)
