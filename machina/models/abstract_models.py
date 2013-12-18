# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db import models

# Local application / specific library imports


class ActiveManager(models.Manager):
    """
    Returns only active objects.
    """
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(is_active__exact=True)


class ActiveModel(models.Model):
    """
    An abstract base class model that provides an is_active field and attach an ActiveManager.
    """
    is_active = models.BooleanField(default=True, db_index=True)

    # Managers
    objects = models.Manager()
    active = ActiveManager()

    class Meta:
        abstract = True


class DatedModel(models.Model):
    """
    An abstract base class model that provides a created and a updated fields to store creation date and last updated date.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
