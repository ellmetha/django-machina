"""
    Forum attachments models
    ========================

    This module defines models provided by the ``forum_attachments`` application.

"""

from machina.apps.forum_conversation.forum_attachments.abstract_models import AbstractAttachment
from machina.core.db.models import model_factory


Attachment = model_factory(AbstractAttachment)
