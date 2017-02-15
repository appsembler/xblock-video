"""
Video xblock helpers.
"""

from HTMLParser import HTMLParser
import pkg_resources

from django.template import Template, Context


html_parser = HTMLParser()  # pylint: disable=invalid-name


def resource_string(path):
    """
    Handy helper for getting resources from our kit.
    """
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


def render_resource(path, **context):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    html = Template(resource_string(path))
    return html_parser.unescape(
        html.render(Context(context))
    )


def ugettext(text):
    """
    Dummy ugettext method that doesn't do anything.
    """
    return text
