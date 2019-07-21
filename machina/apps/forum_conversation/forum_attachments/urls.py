"""
    Forum attachments URLs
    ======================

    This module defines URL patterns associated with the django-machina's ``forum_attachments``
    application.

"""

from django.urls import path

from machina.core.loading import get_class
from machina.core.urls import URLPatternsFactory


class ForumAttachmentsURLPatternsFactory(URLPatternsFactory):
    """ Allows to generate the URL patterns of the ``forum_attachments`` application. """

    attachment_view = get_class('forum_conversation.forum_attachments.views', 'AttachmentView')

    def get_urlpatterns(self):
        """ Returns the URL patterns managed by the considered factory / application. """
        return [
            path('attachment/<int:pk>/', self.attachment_view.as_view(), name='attachment'),
        ]


urlpatterns_factory = ForumAttachmentsURLPatternsFactory()
