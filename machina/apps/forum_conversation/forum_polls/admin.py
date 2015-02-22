# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.contrib import admin

# Local application / specific library imports
from machina.core.db.models import get_model

TopicPoll = get_model('forum_polls', 'TopicPoll')
TopicPollOption = get_model('forum_polls', 'TopicPollOption')
TopicPollVote = get_model('forum_polls', 'TopicPollVote')


class TopicPollOptionInline(admin.TabularInline):
    model = TopicPollOption
    extra = 1


class TopicPollOptionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'poll', 'text',)
    search_fields = ('text',)


class TopicPollAdmin(admin.ModelAdmin):
    inlines = (TopicPollOptionInline,)
    list_display = ('topic', 'duration', 'max_options', 'user_changes',)
    list_filter = ('created', 'updated',)
    search_fields = ('topic__subject',)


class TopicPollVoteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'voter',)


admin.site.register(TopicPoll, TopicPollAdmin)
admin.site.register(TopicPollOption, TopicPollOptionAdmin)
admin.site.register(TopicPollVote, TopicPollVoteAdmin)
