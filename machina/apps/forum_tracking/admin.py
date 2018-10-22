"""
    Forum tracking model admin definitions
    ======================================

    This module defines admin classes used to populate the Django administration dashboard.

"""

from django.contrib import admin

from machina.core.db.models import get_model


ForumReadTrack = get_model('forum_tracking', 'ForumReadTrack')
TopicReadTrack = get_model('forum_tracking', 'TopicReadTrack')


class ForumReadTrackAdmin(admin.ModelAdmin):
    """ The Forum Read Track model admin. """

    list_display = ('__str__', 'user', 'forum', 'mark_time',)
    list_filter = ('mark_time',)


class TopicReadTrackAdmin(admin.ModelAdmin):
    """ The Topic Read Track model admin. """

    list_display = ('__str__', 'user', 'topic', 'mark_time',)
    list_filter = ('mark_time',)


admin.site.register(ForumReadTrack, ForumReadTrackAdmin)
admin.site.register(TopicReadTrack, TopicReadTrackAdmin)
