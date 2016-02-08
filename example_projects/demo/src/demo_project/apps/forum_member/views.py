# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_member.views import ForumProfileUpdateView as BaseForumProfileUpdateView

from demo_project.core.mixins import MenuItemMixin


class ForumProfileUpdateView(MenuItemMixin, BaseForumProfileUpdateView):
    menu_parameters = 'profile'
