import re

import jinja2

from core.config import settings


def ljust(value, width):
    return f"{value:<{width}}"


def rjust(value, width):
    return f"{value:>{width}}"


def render_template(template_name: str, data: dict | None = None) -> str:
    if data is None:
        data = {}
    template = _get_template_env().get_template(template_name)
    rendered = template.render(**data).replace("\n", " ")
    rendered = rendered.replace("<br>", "\n")
    rendered = re.sub(" +", " ", rendered).replace(" .", ".").replace(" ,", ",")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    rendered = rendered.replace("{FOURPACES}", "    ")
    return rendered


def _get_template_env():
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=settings.bot.templates)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        env.filters['ljust'] = ljust
        env.filters['rjust'] = rjust
        _get_template_env.template_env = env

    return _get_template_env.template_env

