
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import HTMLResponse

from utils.logger import logger
from utils.templates import render_web_template

html_router = APIRouter()

@html_router.get("/entrypoint", response_class=HTMLResponse)
async def entrypoint(request: Request, next_route: str = "/"):
    try:
        return HTMLResponse(
            content=render_web_template('entrypoint/template.j2', {"next": next_route}),
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"undefined_error")

