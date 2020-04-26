"""
    Forum abstract models
    =====================

    This module defines abstract models provided by the ``forum`` application.

"""

import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.encoding import force_str
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from machina.apps.forum import signals
from machina.conf import settings as machina_settings
from machina.models import DatedModel
from machina.models.fields import ExtendedImageField, MarkupTextField


def get_forum_image_upload_to(instance, filename):
    """ Returns a valid upload path for an image file associated with a forum instance. """
    return instance.get_image_upload_to(filename)


class AbstractForum(MPTTModel, DatedModel):
    """ The main forum model.

    The tree hierarchy of forums and categories is managed by the MPTTModel which is part of
    django-mptt.

    """

    parent = TreeForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.CASCADE,
        verbose_name=_('Parent'),
    )

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=255, verbose_name=_('Slug'))

    description = MarkupTextField(verbose_name=_('Description'), null=True, blank=True)

    # A forum can come with an image (eg. a small logo)
    image = ExtendedImageField(
        null=True, blank=True, upload_to=get_forum_image_upload_to,
        verbose_name=_('Forum image'), **machina_settings.DEFAULT_FORUM_IMAGE_SETTINGS
    )

    # Forums can be simple links (eg. wiki, documentation, etc)
    link = models.URLField(verbose_name=_('Forum link'), null=True, blank=True)
    link_redirects = models.BooleanField(
        default=False, verbose_name=_('Track link redirects count'),
        help_text=_('Records the number of times a forum link was clicked'),
    )

    # Category, Default forum or Link ; that's what a forum can be
    FORUM_POST, FORUM_CAT, FORUM_LINK = 0, 1, 2
    TYPE_CHOICES = (
        (FORUM_POST, _('Default forum')),
        (FORUM_CAT, _('Category forum')),
        (FORUM_LINK, _('Link forum')),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES, verbose_name=_('Forum type'), db_index=True,
    )

    # Tracking data (only approved topics and posts are recorded)
    direct_posts_count = models.PositiveIntegerField(
        editable=False, blank=True, default=0, verbose_name=_('Direct number of posts'),
    )
    direct_topics_count = models.PositiveIntegerField(
        editable=False, blank=True, default=0, verbose_name=_('Direct number of topics'),)
    link_redirects_count = models.PositiveIntegerField(
        editable=False, blank=True, default=0, verbose_name=_('Track link redirects count'),
    )

    # The 'last_post' and 'last_post_on' fields contain values related to the direct topics/posts
    # only (that is the topics/posts that are directly associated with the considered forum and not
    # one of its sub-forums).
    last_post = models.ForeignKey(
        'forum_conversation.Post', editable=False, related_name='+', blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_('Last post'),
    )
    last_post_on = models.DateTimeField(verbose_name=_('Last post added on'), blank=True, null=True)

    # Display options ; these fields can be used to alter the display of the forums in the list of
    # forums.
    display_sub_forum_list = models.BooleanField(
        default=True, verbose_name=_('Display in parent-forums legend'),
        help_text=_('Displays this forum on the legend of its parent-forum (sub forums list)'),
    )

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
        """ Returns a margin value computed from the forum node's level.

        Used in templates or menus to create an easy-to-see left margin to contrast a forum from
        their parents.

        """
        return self.level * 2

    @property
    def is_category(self):
        """ Returns ``True`` if the forum is a category. """
        return self.type == self.FORUM_CAT

    @property
    def is_forum(self):
        """ Returns ``True`` if the forum is a a default forum. """
        return self.type == self.FORUM_POST

    @property
    def is_link(self):
        """ Returns ``True`` if the forum is a link. """
        return self.type == self.FORUM_LINK

    def clean(self):
        """ Validates the forum instance. """
        super().clean()

        if self.parent and self.parent.is_link:
            raise ValidationError(_('A forum can not have a link forum as parent'))

        if self.is_category and self.parent and self.parent.is_category:
            raise ValidationError(_('A category can not have another category as parent'))

        if self.is_link and not self.link:
            raise ValidationError(_('A link forum must have a link associated with it'))

    def get_image_upload_to(self, filename):
        """ Returns the path to upload a new associated image to. """
        dummy, ext = os.path.splitext(filename)
        return os.path.join(
            machina_settings.FORUM_IMAGE_UPLOAD_TO,
            '{id}{ext}'.format(id=str(uuid.uuid4()).replace('-', ''), ext=ext),
        )

    def save(self, *args, **kwargs):
        """ Saves the forum instance. """
        # It is vital to track the changes of the parent associated with a forum in order to
        # maintain counters up-to-date and to trigger other operations such as permissions updates.
        old_instance = None
        if self.pk:
            old_instance = self.__class__._default_manager.get(pk=self.pk)

        # Update the slug field
        self.slug = slugify(force_str(self.name), allow_unicode=True)

        # Do the save
        super().save(*args, **kwargs)

        # If any change has been made to the forum parent, trigger the update of the counters
        if old_instance and old_instance.parent != self.parent:
            self.update_trackers()
            # Trigger the 'forum_moved' signal
            signals.forum_moved.send(sender=self, previous_parent=old_instance.parent)

    def update_trackers(self):
        """ Updates the denormalized trackers associated with the forum instance. """
        direct_approved_topics = self.topics.filter(approved=True).order_by('-last_post_on')

        # Compute the direct topics count and the direct posts count.
        self.direct_topics_count = direct_approved_topics.count()
        self.direct_posts_count = direct_approved_topics.aggregate(
            total_posts_count=Sum('posts_count'))['total_posts_count'] or 0

        # Forces the forum's 'last_post' ID and 'last_post_on' date to the corresponding values
        # associated with the topic with the latest post.
        if direct_approved_topics.exists():
            self.last_post_id = direct_approved_topics[0].last_post_id
            self.last_post_on = direct_approved_topics[0].last_post_on
        else:
            self.last_post_id = None
            self.last_post_on = None

        # Any save of a forum triggered from the update_tracker process will not result in checking
        # for a change of the forum's parent.
        self._simple_save()

    def _simple_save(self, *args, **kwargs):
        """ Simple wrapper around the standard save method.

        Calls the parent save method in order to avoid the checks for forum parent changes which can
        result in triggering a new update of the counters associated with the current forum.

        This allow the database to not be hit by such checks during very common and regular
        operations such as those provided by the update_trackers function; indeed these operations
        will never result in an update of a forum parent.

        """
        super().save(*args, **kwargs)
