# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db import models

# Local application / specific library imports
from machina.apps.conversation.abstract_models import AbstractTopic


class Topic(AbstractTopic):
    dummy = models.CharField(max_length=128, null=True, blank=True)


from machina.apps.conversation.models import *
