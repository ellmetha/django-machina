"""
    Forum attachments cache
    =======================

    This module defines an abstraction allowing to put forum attachments into cache when users are
    creating forum posts and topics.

"""

from io import BytesIO

from django.conf import settings
from django.core.cache import InvalidCacheBackendError, caches
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils.datastructures import MultiValueDict

from machina.conf import settings as machina_settings


class AttachmentCache:
    """ The attachments cache.

    This one should be used with a FileBasedCache backend. But this can be overriden. The
    attachments cache acts as a wrapper and ensure that the states (name, size, content type,
    charset and content) of all files from any request.FILES dict are saved inside the considered
    backend when calling the 'set' method. Conversely, the 'get' method will populate a dictionary
    of InMemoryUploadedFile instances or TemporaryUploadedFile instancesby using these states.

    """
    def __init__(self):
        self.backend = self.get_backend()

    def get_backend(self):
        """ Returns the associated cache backend. """
        try:
            cache = caches[machina_settings.ATTACHMENT_CACHE_NAME]
        except InvalidCacheBackendError:
            raise ImproperlyConfigured(
                'The attachment cache backend ({}) is not configured'.format(
                    machina_settings.ATTACHMENT_CACHE_NAME,
                ),
            )
        return cache

    def set(self, key, files):
        """ Stores the state of each file embedded in the request.FILES MultiValueDict instance.

        This instance is assumed to be passed as the 'files' argument. Each state stored in the
        cache is a dictionary containing the following values:

            name
                The name of the uploaded file.
            size
                The size of the uploaded file.
            content_type
                The content type of the uploaded file.
            content_length
                The content length of the uploaded file.
            charset
                The charset of the uploaded file.
            content
                The content of the uploaded file.

        """
        files_states = {}

        for name, upload in files.items():
            # Generates the state of the file
            state = {
                'name': upload.name,
                'size': upload.size,
                'content_type': upload.content_type,
                'charset': upload.charset,
                'content': upload.file.read(),
            }
            files_states[name] = state

            # Go to the first byte in the file for future use
            upload.file.seek(0)
        self.backend.set(key, files_states)

    def get(self, key):
        """ Regenerates a MultiValueDict instance containing the files related to all file states
            stored for the given key.
        """
        upload = None
        files_states = self.backend.get(key)
        files = MultiValueDict()
        if files_states:
            for name, state in files_states.items():
                f = BytesIO()
                f.write(state['content'])

                # If the post is too large, we cannot use a
                # InMemoryUploadedFile instance.
                if state['size'] > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                    upload = TemporaryUploadedFile(
                        state['name'],
                        state['content_type'],
                        state['size'],
                        state['charset'],
                    )
                    upload.file = f
                else:
                    f = BytesIO()
                    f.write(state['content'])
                    upload = InMemoryUploadedFile(
                        file=f,
                        field_name=name,
                        name=state['name'],
                        content_type=state['content_type'],
                        size=state['size'],
                        charset=state['charset'],
                    )
                files[name] = upload

                # Go to the first byte in the file for future use
                upload.file.seek(0)

        return files

    def delete(self, key):
        """ Deletes a file associated with a specific key. """
        self.backend.delete(key)


cache = AttachmentCache()
