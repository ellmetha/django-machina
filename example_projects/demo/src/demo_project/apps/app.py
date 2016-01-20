# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from machina.app import BoardApp

# Local application / specific library imports
from demo_project.apps.auth.app import application as auth_app


class DemoForumApp(BoardApp):
    name = None
    auth_app = auth_app

    def get_urls(self):
        urls = super(DemoForumApp, self).get_urls()
        return urls + [
            url(_(r'^account/'), include(self.auth_app.urls)),
        ]


application = DemoForumApp()
