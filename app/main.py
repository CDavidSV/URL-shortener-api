# Imports
from typing import Annotated
from fastapi import Depends, FastAPI
from dotenv import load_dotenv
load_dotenv()

from .routers import api_v1, login, pages

# App
app = FastAPI()

# Routes
app.include_router(api_v1.router)
app.include_router(login.router)
app.include_router(pages.router)