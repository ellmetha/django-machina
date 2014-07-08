# -*- coding: utf-8 -*-

# Standard library imports
import os

# Third party imports
# Local application / specific library imports


MACHINA_VANILLA_APPS = [
    'machina',
    'machina.apps.forum',
    'machina.apps.conversation',
    'machina.apps.conversation.polls',
    'machina.apps.feeds',
    'machina.apps.search',
    'machina.apps.tracking',
    'machina.apps.member',
    'machina.apps.permission',
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
