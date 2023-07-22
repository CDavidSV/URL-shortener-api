from fastapi import APIRouter, Request
from fastapi.responses import  RedirectResponse
from fastapi.templating import Jinja2Templates
from .. import database as db

import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
DB_NAME = os.getenv("DB_NAME")

@router.get("/{back_half_id}")
async def access_page(back_half_id: str, request: Request):
    short_url = db.execute_query("shorturls.db", "SELECT * FROM ShortURL WHERE ShortURLId = ?", (back_half_id,))
    if len(short_url) == 0:
        return templates.TemplateResponse("page_not_found.html", {"request": request})
    
    # Increment the number of times the short url has been accessed.
    db.execute_query(DB_NAME, "UPDATE ShortURL SET ViewCount = ? WHERE ShortURLId = ?", (short_url[0][4] + 1, back_half_id,), True)
    
    # Redirect to the original URL.
    return RedirectResponse(url=short_url[0][1], status_code=302)
