# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import VERSION as DJANGO_VERSION
from django.db import models

# Local application / specific library imports


class ApprovedManager(models.Manager):
    def get_queryset(self):
        """
        Returns all the approved topics or posts.
        """
        parent_self = super(ApprovedManager, self)

        # Handles 'get_query_set' deprecation
        get_queryset = (parent_self.get_queryset
                        if hasattr(parent_self, 'get_queryset')
                        else parent_self.get_query_set)

        qs = get_queryset()
        qs = qs.filter(approved=True)

        return qs

    if DJANGO_VERSION < (1, 6):  # pragma: no cover
        get_query_set = get_queryset
