"""
Video xblock helpers.
"""

from HTMLParser import HTMLParser
import os.path
import pkg_resources

from django.template import Engine, Context, Template


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


def render_template(template_name, **context):
    """
    Render static resource using provided context.

    Returns: django.utils.safestring.SafeText
    """
    template_dirs = [os.path.join(os.path.dirname(__file__), 'static/html')]
    engine = Engine(dirs=template_dirs, debug=True)
    html = engine.get_template(template_name)

    return html_parser.unescape(
        html.render(Context(context))
    )


def ugettext(text):
    """
    Dummy ugettext method that doesn't do anything.
    """
    return text


def underscore_to_mixedcase(value):
    """
    Convert variables with under_score to mixedCase style.
    """
    def mixedcase():
        """Mixedcase generator."""
        yield str.lower
        while True:
            yield str.capitalize

    mix = mixedcase()
    return "".join(mix.next()(x) if x else '_' for x in value.split("_"))
