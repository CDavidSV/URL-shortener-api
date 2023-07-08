# Imports
from fastapi import Depends, FastAPI, Request
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import os
load_dotenv()

from .routers import api_v1, login, pages

class NotAuthenticated(Exception):
    pass

# App
app = FastAPI()

script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

@app.exception_handler(NotAuthenticated)
def auth_exception_handler(request: Request, exc: NotAuthenticated):
    return RedirectResponse(url='/login')

# Routes
app.include_router(api_v1.router)
app.include_router(login.router)
app.include_router(pages.router)