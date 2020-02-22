from django.utils.encoding import smart_str
from markdown2 import markdown as _markdown


def markdown(text, **kwargs):
    return smart_str(_markdown(text, **kwargs).strip())
