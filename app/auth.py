from datetime import datetime, timedelta
from hashlib import sha256
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from . import database as db

import os

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_DAYS = 7
SECRET_KEY = os.getenv("SECRET_JWT_KEY")
DB_NAME = os.getenv("DB_NAME")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    username: str | None = None
    
class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    creation_date: str

class UserInDB(User):
    password_hash: str

def check_password(input_password, hashed_password):
    return hash_password(input_password) == hashed_password

def hash_password(input_):
    return sha256(input_.encode('utf-8')).hexdigest()

def get_user(username: str):
    # Search in the db for the user.
    query = "SELECT * FROM USERS WHERE Username = ?"
    result = db.execute_query("shorturls.db", query, (username,))

    if not len(result) < 1:
        return UserInDB(
            first_name=result[0][1],  # first name
            last_name=result[0][2],   # last name
            email=result[0][0],       # email address
            username=result[0][3],    # username
            creation_date=result[0][5],  # creation date
            password_hash=result[0][4]  # password hash
        )
    
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user is None:
        return False
    if not check_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expiration_delta: timedelta | None = None):
    to_encode = data.copy()
    if expiration_delta:
        expire = datetime.utcnow() + expiration_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt # Return the token for that user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user
