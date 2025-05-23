import os

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from starlette.staticfiles import StaticFiles

from core.config import settings
from utils.logger import logger
from web_app.error_handlers import http_exception_handler, generic_exception_handler
from web_app.routes.images import api_router as images_api_router, html_router as images_html_router
from web_app.routes.users import api_router as users_api_router, html_router as users_html_router
from web_app.routes.entrypoint import html_router as entrypoint_html_router


app = FastAPI()
img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), str(settings.images.path)))
app.mount("/images", StaticFiles(directory=img_dir), name="images")
app.mount("/templates", StaticFiles(directory=settings.web_app.templates), name="templates")

app.include_router(images_api_router)
app.include_router(images_html_router)
app.include_router(users_api_router)
app.include_router(users_html_router)
app.include_router(entrypoint_html_router)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


if __name__ == "__main__":
    logger.info("Initializing FastAPI server...")
    uvicorn.run(
        "web_app.main:app",
        host=settings.web_app.host,
        port=settings.web_app.port,
        reload=False
    )
