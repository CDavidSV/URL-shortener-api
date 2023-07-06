# Imports
from typing import Annotated
from fastapi import Depends, FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
load_dotenv()

from .routers import api_v1, login, pages

# App
app = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

# Routes
app.include_router(api_v1.router)
app.include_router(login.router)
app.include_router(pages.router)