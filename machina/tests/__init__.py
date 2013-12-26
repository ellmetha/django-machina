# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db import models

# Local application / specific library imports
from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField


RESIZED_IMAGE_WIDTH = 100
RESIZED_IMAGE_HEIGHT = 100


class TestableModel(models.Model):
    """
    This model will be used for testing purposes only.
    """
    content = MarkupTextField(null=True, blank=True)
    resized_image = ExtendedImageField(upload_to='machina/test_images',
                                       width=RESIZED_IMAGE_WIDTH, height=RESIZED_IMAGE_HEIGHT,
                                       null=True, blank=True)
    validaded_image = ExtendedImageField(upload_to='machina/test_images',
                                         min_width=100, max_width=120,
                                         min_height=100, max_height=120,
                                         max_upload_size=20000,
                                         null=True, blank=True)


# Sub-packages imports
from test_conversation import *
from test_fields import *
from test_forum import *
