from django import template
from django.conf import settings
from scra_core.release import __version__

import markdown
import mdx_math

register = template.Library()

# see https://python-markdown.github.io/reference/#extensions
md_ext = mdx_math.MathExtension(enable_dollar_delimiter=True)
md = markdown.Markdown(extensions=["extra", md_ext])


@register.filter
def render_markdown(txt):
    return md.convert(txt)


@register.filter
def get_version(_):
    return __version__


@register.filter
def get_last_deployment(_):

    last_deployment = getattr(settings, "LAST_DEPLOYMENT", "<not available>")
    return last_deployment


# maybe a restart of the server is neccessary after chanching this file
