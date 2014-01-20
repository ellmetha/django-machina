# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.db.models import Q
from guardian.core import ObjectPermissionChecker

# Local application / specific library imports


class PermissionHandler(object):
    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that can be seen or read
        by the specified user (at least).
        """
        checker = ObjectPermissionChecker(user)

        # Any superuser should see all the forums
        if user.is_superuser:
            return qs

        # Isolates the top-level forums and check whether they can
        # be viewed by the given user.
        toplevel_forums = qs.filter(parent__isnull=True)
        forums_to_hide = []
        for forum in toplevel_forums:
            if not checker.has_perm('can_see_forum', forum) and not checker.has_perm('can_read_forum', forum):
                forums_to_hide.append(forum.id)

        return qs.exclude(Q(id__in=forums_to_hide) | Q(parent__id__in=forums_to_hide))
