# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django

# Local application / specific library imports
from machina.apps.forum_member.abstract_models import AbstractForumProfile
from machina.core.db.models import model_factory


ForumProfile = model_factory(AbstractForumProfile)


if django.VERSION < (1, 7):  # pragma: no cover
    from . import receivers  # noqa
