# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf.urls import patterns

# Local application / specific library imports
from machina.core.app import Application


class BoardApp(Application):
    name = None

    def get_urls(self):
        return patterns('')


board = application = BoardApp()
