from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


# PILImage
try:
    # Try from the Pillow (or one variant of PIL) install location first.
    from PIL import Image as PILImage
except ImportError:  # pragma: no cover
    try:
        # If that failed, try the alternate import syntax for PIL.
        import Image as PILImage  # noqa
    except ImportError as err:
        # Neither worked, so it's likely not installed.
        raise ImproperlyConfigured(
            _('Neither Pillow nor PIL could be imported: {}').format(err)
        )
