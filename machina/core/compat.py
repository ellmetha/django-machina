# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import VERSION as DJANGO_VESION
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


# PILImage
try:
    # Try from the Pillow (or one variant of PIL) install location first.
    from PIL import Image as PILImage
except ImportError as err:  # pragma: no cover
    try:
        # If that failed, try the alternate import syntax for PIL.
        import Image as PILImage  # noqa
    except ImportError as err:
        # Neither worked, so it's likely not installed.
        raise ImproperlyConfigured(
            _('Neither Pillow nor PIL could be imported: {}').format(err)
        )


# Slugify with 'allow_unicode' option
if DJANGO_VESION < (1, 9):
    import re
    import unicodedata

    from django.utils import six
    from django.utils.encoding import force_text
    from django.utils.functional import allow_lazy
    from django.utils.safestring import mark_safe
    from django.utils.safestring import SafeText

    # Orginally comes from https://github.com/django/django/blob/1.9/django/utils/text.py#L413-L427
    # for compatibility reasons.
    def slugify(value, allow_unicode=False):
        """
        Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
        Remove characters that aren't alphanumerics, underscores, or hyphens.
        Convert to lowercase. Also strip leading and trailing whitespace.
        """
        value = force_text(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
            value = re.sub('[^\w\s-]', '', value, flags=re.U).strip().lower()
            return mark_safe(re.sub('[-\s]+', '-', value, flags=re.U))
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return mark_safe(re.sub('[-\s]+', '-', value))
    slugify = allow_lazy(slugify, six.text_type, SafeText)
else:
    from django.utils.text import slugify


# MiddlewareMixin
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # pragma: no cover
    class MiddlewareMixin(object):
        pass
