# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.conversation.abstract_models import AbstractAttachment
from machina.apps.conversation.abstract_models import AbstractPost
from machina.apps.conversation.abstract_models import AbstractTopic


class Topic(AbstractTopic):
    pass


class Post(AbstractPost):
    pass


class Attachment(AbstractAttachment):
    pass


from .receivers import *
