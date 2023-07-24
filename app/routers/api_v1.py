from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, status, HTTPException
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from app import auth
from .. import database as db
from re import match
from random import choice

import os
import io
import qrcode

class CreateURLData(BaseModel):
    title: str | None
    back_half: str | None
    original_URL: str

class UpdateURLData(BaseModel):
    title: str | None
    back_half: str | None
    original_URL: str | None 

class UpdateShortURL(BaseModel):
    id: str
    content: UpdateURLData

class ShortURL(BaseModel):
    title: str
    back_half: str
    original_URL: str
    creation_date: str
    times_visited: int

DB_NAME = os.getenv("DB_NAME")
router = APIRouter()

def validate_back_half(back_half: str):
    # test a regex here to make sure the back_half is only alphanumeric characters.
    pattern  = "^[a-zA-Z0-9_]{1,255}$"
    if match(pattern, back_half):
        return True
    return False

def new_url_identifier():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    while True:
        identifier = ""
        for i in range(0, 10):
            character = choice(characters)
            identifier += character

        exists = db.execute_query(DB_NAME, "SELECT * FROM ShortURL WHERE ShortURLId = ?", (identifier,))
        if len(exists) == 0:
            break

    return identifier

def validate_user_permision(usernameCurrent, usernameOwner):
    return usernameCurrent == usernameOwner

def is_empty_or_None(string: str):
    return string is None or string == ""

# Shortened url creation and deletion.
@router.post("/api/v1/urls/create")
async def create_shortened_url(current_user: Annotated[auth.User, Depends(auth.get_current_user)], new_url_info: CreateURLData):
    creation_date = str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().day)
    
    if is_empty_or_None(new_url_info.back_half):
        # Create a random identifier for the back_half of the new short url.
        identifier = new_url_identifier()
        db.execute_query(DB_NAME, "INSERT INTO ShortURL values(?,?,?,?,?,?)", (new_url_info.title, new_url_info.original_URL, identifier, creation_date, 0, current_user.username), True)
        return { "detail": "Short URL created successfully" }
    
    if not validate_back_half(new_url_info.back_half):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Back half of URL must be alphanumeric between 1 and 255 characters"
        )

    # Check if the back_half already exists in the database.
    exists = db.execute_query(DB_NAME, "SELECT * FROM ShortURL WHERE ShortURLId = ?", (new_url_info.back_half,))
    if len(exists) >= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Short URL already exists"
        )

    # Create the new short url.
    db.execute_query(DB_NAME, "INSERT INTO ShortURL values(?,?,?,?,?,?)", ("" if is_empty_or_None(new_url_info.title) else new_url_info.title, new_url_info.original_URL, new_url_info.back_half, creation_date, 0, current_user.username), True)

    return { "detail": "Short URL created successfully" }

@router.delete("/api/v1/urls/delete")
async def delete_shortened_url(current_user: Annotated[auth.User, Depends(auth.get_current_user)], url_id: str):
    # Find the url in the database.
    row = db.execute_query(DB_NAME, 'SELECT * FROM ShortURL WHERE ShortURLId = ?', (url_id,))

    # verify that the url exists and if the user has permission to delete it.
    if len(row) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This url does not exist"
        )
    
    if not validate_user_permision(current_user.username, row[0][5]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to delete this url"
        )
    
    # Delete the url from the database.
    db.execute_query(DB_NAME, "DELETE FROM ShortURL WHERE ShortURLId = ?", (url_id,), True)
    return { "detail": "URL deleted successfully" }

@router.post("/api/v1/urls/update")
async def update_url(current_user: Annotated[auth.User, Depends(auth.get_current_user)], data: UpdateShortURL):
    row = db.execute_query(DB_NAME, 'SELECT * FROM ShortURL WHERE ShortURLId = ?', (data.id,))

    if len(row) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This url does not exist"
        )
    
    if not validate_user_permision(current_user.username, row[0][5]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unable to delete this url"
        )
    
    if data.content.back_half and not validate_back_half(data.content.back_half):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Back half of URL must be alphanumeric between 1 and 255 characters"
        )

    short_url = ShortURL(
        title=row[0][0],
        back_half=row[0][2],
        original_URL=row[0][1],
        creation_date=row[0][3],
        times_visited=row[0][4]
    )
    
    updated_short_url = ShortURL(
        title=data.content.title if not is_empty_or_None(data.content.title) else short_url.title,
        back_half=data.content.back_half if not is_empty_or_None(data.content.back_half) else short_url.back_half,
        original_URL=data.content.original_URL if not is_empty_or_None(data.content.original_URL) else short_url.original_URL,
        creation_date=short_url.creation_date,
        times_visited=short_url.times_visited
    )

    db.execute_query(DB_NAME, "UPDATE ShortURL SET Title = ?, OriginalUrl = ?, ShortURLId = ? WHERE ShortURLId = ?", (updated_short_url.title, updated_short_url.original_URL, updated_short_url.back_half, data.id), True)
    return { "detail": "Data updated", "updatedData": updated_short_url }

@router.get("/api/v1/urls")
async def get_urls(current_user: Annotated[auth.User, Depends(auth.get_current_user)]):
    rows = db.execute_query(DB_NAME, "SELECT * FROM ShortURL WHERE User = ?", (current_user.username,))

    if len(rows) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not created any short urls"
        )
    
    urls = []
    for row in rows:
        urls.append(
            ShortURL(
                title=row[0],
                back_half=row[2],
                original_URL=row[1],
                creation_date=row[3],
                times_visited=row[4]
        )
    )
    
    return { "detail": "success", "item_count": len(urls),"short_urls": urls, "user": current_user.username }

@router.get("/api/v1/urls/{url_id}/qr")
async def get_qr(current_user: Annotated[auth.User, Depends(auth.get_current_user)], url_id: str):
    short_url = db.execute_query(DB_NAME, 'SELECT * FROM ShortURL WHERE ShortURLID = ?', (url_id,))

    if len(short_url) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This url does not exist"
        )

    qr = qrcode.QRCode()
    qr.add_data(short_url[0][1])
    qr_img = qr.make_image(fill_color="black", back_color="white")

    img_io = io.BytesIO()
    qr_img.save(img_io, "PNG")
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")

@router.get("/api/v1/urls/{url_id}/info")
async def get_short_url_info(current_user: Annotated[auth.User, Depends(auth.get_current_user)], url_id: str):
    row = db.execute_query(DB_NAME, "SELECT * FROM ShortURL WHERE ShortURLId = ?", (url_id,))

    if len(row) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This url does not exist"
        )
    
    short_url = ShortURL(
        title=row[0][0],
        back_half=row[0][2],
        original_URL=row[0][1],
        creation_date=row[0][3],
        times_visited=row[0][4]
    )

    return { "detail": "success", "data": short_url, "owner": row[0][5] } 