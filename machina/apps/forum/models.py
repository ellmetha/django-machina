# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.forum.abstract_models import AbstractForum
from machina.apps.forum.abstract_models import AbstractForumReadTrack


class Forum(AbstractForum):
    pass


class ForumReadTrack(AbstractForumReadTrack):
    pass


from receivers import *
