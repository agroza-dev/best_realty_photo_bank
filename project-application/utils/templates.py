import re
import jinja2
from typing import Optional
from core.config import settings


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
        _get_template_env.template_envs[template_path] = env

    return _get_template_env.template_envs[template_path]