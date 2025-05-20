from fastapi import Request, HTTPException, status
from fastapi.responses import HTMLResponse

from utils.templates import render_web_template, render_common_template


async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_400_BAD_REQUEST:
        text = render_common_template('error_user_not_found.j2')
        return HTMLResponse(
            content=render_web_template('errors/restrict_error.j2', {'message': text, 'code': status.HTTP_400_BAD_REQUEST}),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        text = render_common_template('error_user_is_deactivated.j2')
        return HTMLResponse(
            content=render_web_template('errors/restrict_error.j2', {'message': text, 'code': status.HTTP_403_FORBIDDEN}),
            status_code=status.HTTP_403_FORBIDDEN
        )


async def generic_exception_handler(request: Request, exc: Exception):
    return HTMLResponse(
        content="<h1>Произошла непредвиденная ошибка</h1><p>Попробуйте позже.</p>",
        status_code=500,
    )
