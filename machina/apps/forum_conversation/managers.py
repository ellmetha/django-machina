# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db import models

# Local application / specific library imports


class ApprovedManager(models.Manager):
    def get_queryset(self):
        """
        Returns all the approved topics or posts.
        """
        qs = super(ApprovedManager, self).get_queryset()
        qs = qs.filter(approved=True)

        return qs
