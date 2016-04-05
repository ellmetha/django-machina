# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField


RESIZED_IMAGE_WIDTH = 100
RESIZED_IMAGE_HEIGHT = 100
VALIDATED_IMAGE_MIN_WIDTH = 100
VALIDATED_IMAGE_MAX_WIDTH = 120
VALIDATED_IMAGE_MIN_HEIGHT = 100
VALIDATED_IMAGE_MAX_HEIGHT = 120
VALIDATED_IMAGE_MAX_SIZE = 12000


class DummyModel(models.Model):
    """
    This model will be used for testing purposes only.
    """
    content = MarkupTextField(null=True, blank=True)
    resized_image = ExtendedImageField(
        upload_to='machina/test_images', width=RESIZED_IMAGE_WIDTH, height=RESIZED_IMAGE_HEIGHT,
        null=True, blank=True)
    validated_image = ExtendedImageField(
        upload_to='machina/test_images', min_width=VALIDATED_IMAGE_MIN_WIDTH,
        max_width=VALIDATED_IMAGE_MAX_WIDTH, min_height=VALIDATED_IMAGE_MIN_HEIGHT,
        max_height=VALIDATED_IMAGE_MAX_HEIGHT, max_upload_size=VALIDATED_IMAGE_MAX_SIZE, null=True,
        blank=True)

    class Meta:
        app_label = 'tests'
