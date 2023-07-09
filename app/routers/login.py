from datetime import timedelta, date, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from .. import database as db
from .. import auth

import os

class NewUserData(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str


router = APIRouter()
DB_NAME = os.getenv("DB_NAME")

def register_new_user():
    return None

# Manage user creation and logins.
@router.post("/user/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRATION_DAYS)
    access_token = auth.create_access_token(
        data={"sub": user.username }, expiration_delta=access_token_expires
    )

    # Set the JWT token as a cookie
    response.set_cookie(key="AT", value=access_token, httponly=True, expires=datetime.now(timezone.utc) + access_token_expires)
    return {"token": access_token, "token-type": "bearer"}

@router.post("/user/create")
async def create_new_user(new_user: NewUserData, response: Response):
    # Check if the email or username are already taken
    email = db.execute_query(DB_NAME, "SELECT * FROM Users WHERE Email = ?", (new_user.email,))
    username = db.execute_query(DB_NAME, "SELECT * FROM Users WHERE Username = ?", (new_user.username,))
    if len(email) >= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use"
        )
    
    if len(username) >= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already in use"
        )

    password_hash = auth.hash_password(new_user.password)
    creation_date = str(date.today().year) + "-" + str(date.today().month) + "-" + str(date.today().day)
    db.execute_query(DB_NAME, "INSERT INTO Users values(?,?,?,?,?,?)", (new_user.email, new_user.first_name, new_user.last_name, new_user.username, password_hash, creation_date,), True)

    access_token_expires = timedelta(days=auth.ACCESS_TOKEN_EXPIRATION_DAYS)
    access_token = auth.create_access_token(
        data={"sub": new_user.username }, expiration_delta=access_token_expires
    )

    # Set the JWT token as a cookie
    response.set_cookie(key="AT", value=access_token, httponly=True, expires=datetime.now(timezone.utc) + access_token_expires)
    return {"detail": "Account creation successfull", "token": access_token, "token_type": "bearer"}