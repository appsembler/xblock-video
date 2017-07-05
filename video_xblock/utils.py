"""
Video xblock helpers.
"""

from HTMLParser import HTMLParser
from importlib import import_module
from xml.sax.saxutils import unescape
import os.path
import pkg_resources

from django.template import Engine, Context, Template
from xblockutils.resources import ResourceLoader

from .constants import TranscriptSource

html_parser = HTMLParser()  # pylint: disable=invalid-name
loader = ResourceLoader(__name__)  # pylint: disable=invalid-name


def import_from(module, klass):
    """
    Dynamic equivalent for 'from module import klass'.
    """
    return getattr(import_module(module), klass)


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


def remove_escaping(text):
    """
    Clean text from special `escape` symbols.

    Reference: https://wiki.python.org/moin/EscapingHtml.
    """
    html_unescape_table = {
        "&amp;": "&",
        "&quot;": '"',
        "&amp;#39;": "'",
        "&apos;": "'",
        "&gt;": ">",
        "&lt;": "<"
    }
    return unescape(text, html_unescape_table)


def create_reference_name(lang_label, video_id, source="default"):
    """
    Build transcript file reference based on input information.

    Format is <language label>_<source>_captions_video_<video_id>, e.g. "English_default_captions_video_456g68"
    """
    reference = "{lang_label}_{source}_captions_video_{video_id}".format(
        lang_label=lang_label,
        video_id=video_id,
        source=source,
    ).encode('utf8')
    return reference


def filter_transcripts_by_source(transcripts, source=TranscriptSource.DEFAULT):
    """
    Filter given transcripts by source attribute.
    """
    if not transcripts:
        return transcripts
    return (tr for tr in transcripts if tr['source'] == source)


def normalize_transcripts(transcripts):
    """
    Add to manually uploaded transcripts "source" attribute.
    """
    for tr_dict in transcripts:
        tr_dict.setdefault('source', TranscriptSource.MANUAL)
    return transcripts
