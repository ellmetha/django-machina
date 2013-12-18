# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin
from mptt.admin import MPTTModelAdmin

# Local application / specific library imports
from machina.apps.forum.models import Forum


admin.site.register(Forum, MPTTModelAdmin)
