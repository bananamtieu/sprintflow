import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.db.session import init_db
from app.web.routes import router as web_router
from app.core.config import settings

app = FastAPI()

# Sessions (store JWT for the UI)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

# Templates + static assets (paths are relative to where you run uvicorn)
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(api_router, prefix="/api/v1")
app.include_router(web_router)
