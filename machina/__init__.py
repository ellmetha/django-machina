# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
# Local application / specific library imports


MACHINA_VANILLA_APPS = [
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
]


# Main Machina template directory
MACHINA_MAIN_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates/machina')


def get_vanilla_apps(overrides=None):
    """
    Returns a list of machina's apps. Any of these apps can be overriden with
    custom apps specified in the 'overrides' list.
    """
    if not overrides:
        return MACHINA_VANILLA_APPS

    def get_app_label(app_label, overrides):
        pattern = app_label.replace('machina.apps.', '')
        for override in overrides:
            if override.endswith(pattern):
                return override
        return app_label

    apps = [get_app_label(app_label, overrides) for app_label in MACHINA_VANILLA_APPS]
    return apps


pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('django-machina')
__version__ = distribution.version
