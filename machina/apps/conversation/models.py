# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
import django

# Local application / specific library imports
from machina.apps.conversation.abstract_models import AbstractPost
from machina.apps.conversation.abstract_models import AbstractTopic
from machina.core.db.models import model_factory


Topic = model_factory(AbstractTopic)
Post = model_factory(AbstractPost)


if django.VERSION < (1, 7):
    from .receivers import *  # noqa
