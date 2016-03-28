# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _


class DatedModel(models.Model):
    """
    An abstract base class model that provides a created and a updated fields to store creation date
    and last updated date.
    """
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Update date'))

    class Meta:
        abstract = True
