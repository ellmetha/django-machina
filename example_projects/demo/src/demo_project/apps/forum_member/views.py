# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from machina.apps.forum_member.views import ForumProfileUpdateView as BaseForumProfileUpdateView

# Local application / specific library imports
from demo_project.core.mixins import MenuItemMixin


class ForumProfileUpdateView(MenuItemMixin, BaseForumProfileUpdateView):
    menu_parameters = 'profile'
