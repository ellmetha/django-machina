# -*- coding: utf-8 -*-

"""
    Django-machina
    ==============

    Django-machina is a Django forum engine for building powerful community driven websites.

"""

from __future__ import unicode_literals

import os


__version__ = '0.7.0.dev'


MACHINA_VANILLA_APPS = [
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
]


# Main Machina static directory
MACHINA_MAIN_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'static/machina/build')

# Main Machina template directory
MACHINA_MAIN_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'templates/machina')


def get_apps(overrides=None):
    """
    Returns a list of machina's apps. Any of these apps can be overriden with
    custom apps specified in the 'overrides' list.
    """
    if not overrides:
        return MACHINA_VANILLA_APPS

    def _get_app_label(app_label):
        pattern = app_label.replace('machina.apps.', '')
        return next((o for o in overrides if o.endswith(pattern)), app_label)

    return list(map(_get_app_label, MACHINA_VANILLA_APPS))
