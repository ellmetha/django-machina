# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


class ApprovedManager(models.Manager):
    def get_queryset(self):
        """
        Returns all the approved topics or posts.
        """
        qs = super(ApprovedManager, self).get_queryset()
        qs = qs.filter(approved=True)

        return qs
