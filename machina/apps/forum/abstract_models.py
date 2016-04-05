# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

from machina.apps.forum import signals
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.models import DatedModel
from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField

ForumManager = get_class('forum.managers', 'ForumManager')


@python_2_unicode_compatible
class AbstractForum(MPTTModel, DatedModel):
    """
    The main forum model.
    The tree hierarchy of forums and categories is managed by the MPTTModel
    which is part of django-mptt.
    """
    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', verbose_name=_('Parent'))

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=255, verbose_name=_('Slug'))

    description = MarkupTextField(
        verbose_name=_('Description'),
        null=True, blank=True)

    # A forum can come with an image (eg. a small logo)
    image = ExtendedImageField(verbose_name=_('Forum image'), null=True, blank=True,
                               upload_to=machina_settings.FORUM_IMAGE_UPLOAD_TO,
                               **machina_settings.DEFAULT_FORUM_IMAGE_SETTINGS)

    # Forums can be simple links (eg. wiki, documentation, etc)
    link = models.URLField(verbose_name=_('Forum link'), null=True, blank=True)
    link_redirects = models.BooleanField(
        verbose_name=_('Track link redirects count'),
        help_text=_('Records the number of times a forum link was clicked'), default=False)

    # Category, Default forum or Link ; that's what a forum can be
    FORUM_POST, FORUM_CAT, FORUM_LINK = 0, 1, 2
    TYPE_CHOICES = (
        (FORUM_POST, _('Default forum')),
        (FORUM_CAT, _('Category forum')),
        (FORUM_LINK, _('Link forum')),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES, verbose_name=_('Forum type'), db_index=True)

    # Tracking data (only approved topics and posts are recorded)
    posts_count = models.PositiveIntegerField(
        verbose_name=_('Number of posts'), editable=False, blank=True, default=0)
    topics_count = models.PositiveIntegerField(
        verbose_name=_('Number of topics'), editable=False, blank=True, default=0)
    link_redirects_count = models.PositiveIntegerField(
        verbose_name=_('Track link redirects count'), editable=False, blank=True, default=0)
    last_post_on = models.DateTimeField(verbose_name=_('Last post added on'), blank=True, null=True)

    # Display options
    display_sub_forum_list = models.BooleanField(
        verbose_name=_('Display in parent-forums legend'),
        help_text=_('Displays this forum on the legend of its parent-forum (sub forums list)'),
        default=True)

    objects = ForumManager()

    class Meta:
        abstract = True
        app_label = 'forum'
        ordering = ['tree_id', 'lft']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __str__(self):
        return self.name

    @property
    def margin_level(self):
        """
        Used in templates or menus to create an easy-to-see left margin to contrast
        a forum from their parents.
        """
        return self.level * 2

    @property
    def is_category(self):
        """
        Returns True if the forum is a category.
        """
        return self.type == self.FORUM_CAT

    @property
    def is_forum(self):
        """
        Returns True if the forum is a a default forum.
        """
        return self.type == self.FORUM_POST

    @property
    def is_link(self):
        """
        Returns True if the forum is a link.
        """
        return self.type == self.FORUM_LINK

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
        # maintain counters up-to-date and to trigger other operations such as permissions updates.
        old_instance = None
        if self.pk:
            old_instance = self.__class__._default_manager.get(pk=self.pk)

        # Update the slug field
        self.slug = slugify(force_text(self.name))

        # Do the save
        super(AbstractForum, self).save(*args, **kwargs)

        # If any change has been made to the forum parent, trigger the update of the counters
        if old_instance and old_instance.parent != self.parent:
            self.update_trackers()
            # The previous parent trackers should also be updated
            if old_instance.parent:
                old_parent = old_instance.parent
                old_parent.refresh_from_db()
                old_parent.update_trackers()
            # Trigger the 'forum_moved' signal
            signals.forum_moved.send(sender=self, previous_parent=old_instance.parent)

    def _simple_save(self, *args, **kwargs):
        """
        Calls the parent save method in order to avoid the checks for forum parent changes
        which can result in triggering a new update of the counters associated with the
        current forum.
        This allow the database to not be hit by such checks during very common and regular
        operations such as those provided by the update_trackers function; indeed these operations
        will never result in an update of a forum parent.
        """
        super(AbstractForum, self).save(*args, **kwargs)

    def update_trackers(self):
        # Fetch the list of ids of all descendant forums including the current one
        forum_ids = self.get_descendants(include_self=True).values_list('id', flat=True)

        # Determine the list of the associated topics, that is the list of topics
        # associated with the current forum plus the list of all topics associated
        # with the descendant forums.
        topic_klass = get_model('forum_conversation', 'Topic')
        topics = topic_klass.objects.filter(forum__id__in=forum_ids).order_by('-last_post_on')
        approved_topics = topics.filter(approved=True)

        self.topics_count = approved_topics.count()
        # Compute the forum level posts count (only approved posts are recorded)
        posts_count = sum(topic.posts_count for topic in topics)
        self.posts_count = posts_count

        # Force the forum 'last_post_on' date to the one associated with the topic with
        # the latest post.
        self.last_post_on = approved_topics[0].last_post_on if len(approved_topics) else None

        # Any save of a forum triggered from the update_tracker process will not result
        # in checking for a change of the forum's parent.
        self._simple_save()

        # Trigger the parent trackers update if necessary
        if self.parent:
            self.parent.update_trackers()
