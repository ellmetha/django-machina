# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

# Local application / specific library imports
from machina.apps.forum import signals
from machina.conf import settings as machina_settings
from machina.core.loading import get_class
from machina.core.utils import refresh
from machina.models import ActiveModel
from machina.models import DatedModel
from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField

ForumManager = get_class('forum.managers', 'ForumManager')


FORUM_TYPES = Choices(
    (0, 'forum_post', _('Default forum')),
    (1, 'forum_cat', _('Category forum')),
    (2, 'forum_link', _('Link forum')),
)


@python_2_unicode_compatible
class AbstractForum(MPTTModel, ActiveModel, DatedModel):
    """
    The main forum model.
    The tree hierarchy of forums and categories is managed by the MPTTModel
    which is part of django-mptt.
    """
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_('Parent'))

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = MarkupTextField(verbose_name=_('Description'), null=True, blank=True)

    # A forum can come with an image (eg. a small logo)
    image = ExtendedImageField(verbose_name=_('Forum image'), null=True, blank=True,
                               upload_to=machina_settings.FORUM_IMAGE_UPLOAD_TO,
                               **machina_settings.DEFAULT_FORUM_IMAGE_SETTINGS)

    # Forums can be simple links (eg. wiki, documentation, etc)
    link = models.URLField(verbose_name=_('Forum link'), null=True, blank=True)
    link_redirects = models.BooleanField(verbose_name=_('Track link redirects count'),
                                         help_text=_('Records the number of times a forum link was clicked'),
                                         default=False)

    # Category, Default forum or Link ; that's what a forum can be
    TYPE_CHOICES = FORUM_TYPES
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, verbose_name=_('Forum type'), db_index=True)

    # Tracking data
    posts_count = models.PositiveIntegerField(verbose_name=_('Number of posts'), editable=False, blank=True, default=0)
    topics_count = models.PositiveIntegerField(verbose_name=_('Number of topics'), editable=False, blank=True, default=0)
    real_topics_count = models.PositiveIntegerField(verbose_name=_('Number of topics (includes unapproved topics)'),
                                                    editable=False, blank=True, default=0)
    link_redirects_count = models.PositiveIntegerField(verbose_name=_('Track link redirects count'),
                                                       editable=False, blank=True, default=0)

    # Display options
    display_sub_forum_list = models.BooleanField(verbose_name=_('Display in parent-forums legend'),
                                                 help_text=_('Displays this forum on the legend of its parent-forum (sub forums list)'),
                                                 default=True)

    objects = ForumManager()

    class Meta:
        abstract = True
        ordering = ['tree_id', 'lft']
        permissions = [
            # Forums
            ('can_see_forum', _('Can see forum')),
            ('can_read_forum', _('Can read forum')),
            # Topics & posts
            ('can_start_new_topics', _('Can start new topics')),
            ('can_reply_to_topics', _('Can reply to topics')),
            ('can_post_announcements', _('Can post announcements')),
            ('can_post_stickies', _('Can post stickies')),
            ('can_delete_own_posts', _('Can delete own posts')),
            ('can_edit_own_posts', _('Can edit own posts')),
            ('can_attach_file', _('Can attach file')),
            ('can_download_file', _('Can download file')),
            ('can_post_without_approval', _('Can post without approval')),
            # Polls
            ('can_create_poll', _('Can create poll')),
            ('can_vote_in_polls', _('Can vote in polls')),
            ('can_change_existing_vote', ('Can change existing vote')),
            # Moderation
            ('can_close_topics', _('Can close topics')),
            ('can_move_topics', _('Can move topics')),
            ('can_edit_posts', _('Can edit posts')),
            ('can_delete_posts', _('Can delete posts')),
            ('can_move_posts', _('Can move posts')),
        ]
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def margin_level(self):
        """
        Used in templates or menus to create an easy-to-see left margin to contrast
        a forum from their parents.
        """
        return self.level * 2

    @property
    def is_category(self):
        return self.type == FORUM_TYPES.forum_cat

    @property
    def is_forum(self):
        return self.type == FORUM_TYPES.forum_post

    @property
    def is_link(self):
        return self.type == FORUM_TYPES.forum_link

    def clean(self):
        super(AbstractForum, self).clean()

        if self.parent and self.parent.is_link:
                raise ValidationError(_('A forum can not have a link forum as parent'))

        if self.is_category and self.parent and self.parent.is_category:
                raise ValidationError(_('A category can not have another category as parent'))

        if self.is_link and not self.link:
            raise ValidationError(_('A link forum must have a link associated with it'))

    def save(self, *args, **kwargs):
        # It is vital to track the changes of the parent associated with a forum in order to
        # maintain counters up-to-date and to trigger other operations such as permissions updates.
        old_instance = None
        if self.pk:
            old_instance = self.__class__._default_manager.get(pk=self.pk)

        # Do the save
        super(AbstractForum, self).save(*args, **kwargs)

        # If any change has been made to the forum parent, trigger the update of the counters
        if old_instance and old_instance.parent != self.parent:
            self.update_trackers()
            # The previous parent trackers should also be updated
            if old_instance.parent:
                old_parent = refresh(old_instance.parent)
                old_parent.update_trackers()
            # Trigger the 'forum_moved' signal
            signals.forum_moved.send(sender=self, previous_parent=old_instance.parent)

    def _simple_save(self, *args, **kwargs):
        """
        Calls the parent save method in order to avoid the checks for forum parent changes
        which can result in triggering a new update of the counters associated with the
        current forum.
        This allow the database to not be hit by such checks during very common and regular
        operations such as those provided by the update_trackers function; indeed these operations
        will never result in an update of a forum parent.
        This save is done without triggering the update of the 'updated' field by disabling the
        'auto_now' behavior.
        """
        self._meta.get_field_by_name('updated')[0].auto_now = False
        super(AbstractForum, self).save(*args, **kwargs)
        self._meta.get_field_by_name('updated')[0].auto_now = True

    def update_trackers(self):
        # Fetch the list of ids of all descendant forums including the current one
        forum_ids = self.get_descendants(include_self=True).values_list('id', flat=True)

        # Determine the list of the associated topics, that is the list of topics
        # associated with the current forum plus the list of all topics associated
        # with the descendant forums.
        Topic = models.get_model('conversation', 'Topic')
        topics = Topic.objects.filter(forum__id__in=forum_ids).order_by('-updated')
        approved_topics = topics.filter(approved=True)

        self.real_topics_count = topics.count()
        self.topics_count = approved_topics.count()
        # Compute the forum level posts count
        posts_count = sum(topic.posts_count for topic in topics)
        self.posts_count = posts_count

        # Force the forum 'updated' date to the one associated with the last topic updated
        self.updated = approved_topics[0].updated if len(approved_topics) else now()

        # Any save of a forum triggered from the update_tracker process will not result
        # in checking for a change of the forum's parent.
        self._simple_save()

        # Trigger the parent trackers update if necessary
        if self.parent:
            self.parent.update_trackers()

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('forum:forum', kwargs={'pk': str(self.id)})
