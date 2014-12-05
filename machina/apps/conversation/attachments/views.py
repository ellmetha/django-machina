# -*- coding: utf-8 -*-

# Standard library imports
import mimetypes
import os

# Third party imports
from django.http import HttpResponse
from django.views.generic import DetailView

# Local application / specific library imports
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.views.mixins import PermissionRequiredMixin

Attachment = get_model('attachments', 'Attachment')

PermissionHandler = get_class('permission.handler', 'PermissionHandler')
perm_handler = PermissionHandler()


class AttachmentView(PermissionRequiredMixin, DetailView):
    model = Attachment
    permission_required = []  # Defined in the 'perform_permissions_check()' method

    def render_to_response(self, context, **response_kwargs):
        filename = os.path.basename(self.object.file.name)

        # Try to guess the content type of the given file
        content_type, _ = mimetypes.guess_type(self.object.file.name)
        if not content_type:
            content_type = 'text/plain'

        response = HttpResponse(self.object.file, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

        return response

    # Permissions checks

    def get_controlled_object(self):
        """
        Returns the forum associated with the current attachment.
        """
        return self.get_object().post.topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return perm_handler.can_download_files(obj, user)
