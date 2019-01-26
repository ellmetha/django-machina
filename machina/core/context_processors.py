from machina.conf import settings as machina_settings


def metadata(request):
    """ Appends some Machina-specific data to the template context. """
    return {
        'MACHINA_FORUM_NAME': machina_settings.FORUM_NAME,
        'MACHINA_BASE_TEMPLATE_NAME': machina_settings.BASE_TEMPLATE_NAME,
    }
