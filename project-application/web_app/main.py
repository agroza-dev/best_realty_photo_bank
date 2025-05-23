import os

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from core.config import settings
from utils.logger import logger
from web_app.routes.images import api_router as images_api_router, html_router as images_html_router


app = FastAPI()
img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), str(settings.images.path)))
app.mount("/images", StaticFiles(directory=img_dir), name="images")
app.mount("/templates", StaticFiles(directory=settings.web_app.templates), name="templates")


app.include_router(images_api_router)
app.include_router(images_html_router)



if __name__ == "__main__":
    logger.info("Initializing FastAPI server...")
    uvicorn.run(
        "web_app.main:app",
        host=settings.web_app.host,
        port=settings.web_app.port,
        reload=False
    )
