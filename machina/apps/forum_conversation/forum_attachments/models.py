# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_conversation.forum_attachments.abstract_models import AbstractAttachment
from machina.core.db.models import model_factory


Attachment = model_factory(AbstractAttachment)
