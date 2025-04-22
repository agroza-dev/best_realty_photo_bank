import os

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from utils.logger import logger
from web_app.routes import api_router, html_router


app = FastAPI()
img_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../project-application/var/images"))
app.mount("/images", StaticFiles(directory=img_dir), name="images")
app.include_router(html_router)
app.include_router(api_router)


if __name__ == "__main__":
    logger.info("Initializing FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True
    )
