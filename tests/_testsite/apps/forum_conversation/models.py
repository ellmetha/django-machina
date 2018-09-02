from django.db import models
from machina.apps.forum_conversation.abstract_models import AbstractTopic


class Topic(AbstractTopic):
    dummy = models.CharField(max_length=128, null=True, blank=True)


from machina.apps.forum_conversation.models import *  # noqa
