import os
import random
from pathlib import Path
import jinja2
from typing import Optional
from core.config import settings
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

def autoversion_filter(filepath: str) -> str:
    static_file = Path(settings.web_app.templates) / filepath.replace('/templates', '').lstrip("/")
    try:
        mtime = int(os.path.getmtime(static_file))

        return f"{filepath}?v={mtime}"
    except FileNotFoundError:
        return f"{filepath}?v={random.randint(1, 10)}"


def render_common_template(template_name: str, data: Optional[dict] = None) -> str:
    return _render_template(template_name, data, settings.app.templates)


def render_web_template(template_name: str, data: Optional[dict] = None) -> str:
    return _render_template(template_name, data, settings.web_app.templates)


def render_bot_template(template_name: str, data: Optional[dict] = None) -> str:
    return _render_template(template_name, data, settings.bot.templates)


def _render_template(
    template_name: str,
    data: Optional[dict],
    template_path: str,
) -> str:
    if data is None:
        data = {}
    template = _get_template_env(template_path).get_template(template_name)
    rendered = template.render(**data)
    return rendered


def _get_template_env(template_path: str) -> jinja2.Environment:
    if not hasattr(_get_template_env, "template_envs"):
        _get_template_env.template_envs = {}

    if template_path not in _get_template_env.template_envs:
        template_loader = jinja2.FileSystemLoader(searchpath=template_path)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        env.filters["autoversion"] = autoversion_filter

        _get_template_env.template_envs[template_path] = env

    return _get_template_env.template_envs[template_path]