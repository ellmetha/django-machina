# -*- coding: utf-8 -*-

# Standard library imports

# Third party imports

# Local application / specific library imports


MACHINA_VANILLA_APPS = [
    'machina',
    'machina.apps.forum',
    'machina.apps.conversation',
    'machina.apps.member',
]


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

    apps = []
    for app_label in MACHINA_VANILLA_APPS:
        apps.append(get_app_label(app_label, overrides))
    return apps
