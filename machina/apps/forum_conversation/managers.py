"""
    Forum conversation managers
    ===========================

    This module defines model managers related to forum conversation models.

"""

from django.db import models

from machina.conf import settings as machina_settings


class ApprovedManager(models.Manager):
    def get_queryset(self):
        """ Returns all the approved topics or posts. """
        qs = super().get_queryset()
        qs = qs.filter(machina_settings.APPROVED_FILTER)
        return qs
