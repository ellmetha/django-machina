# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals

# Third party imports
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from mptt.models import MPTTModel
from mptt.models import TreeForeignKey

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.models import ActiveModel
from machina.models.fields import ExtendedImageField
from machina.models.fields import MarkupTextField


FORUM_TYPES = Choices(
    (0, 'forum_post', _('Default forum')),
    (1, 'forum_cat', _('Category forum')),
    (2, 'forum_link', _('Link forum')),
)


class AbstractForum(MPTTModel, ActiveModel):
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
    type = models.PositiveSmallIntegerField(choices=FORUM_TYPES, verbose_name=_('Forum type'), db_index=True)

    # Tracking data
    posts_count = models.PositiveIntegerField(verbose_name=_('Number of posts'), editable=False, blank=True, default=0)
    topics_count = models.PositiveIntegerField(verbose_name=_('Number of topics'), editable=False, blank=True, default=0)
    real_topics_count = models.PositiveIntegerField(verbose_name=_('Number of topics (includes unapproved topics)'),
                                                    editable=False, blank=True, default=0)
    link_redirects_count = models.PositiveIntegerField(verbose_name=_('Track link redirects count'),
                                                       editable=False, blank=True, default=0)

    # Display options
    display_on_index = models.BooleanField(verbose_name=_('Display on index'), default=True)
    display_sub_forum_list = models.BooleanField(verbose_name=_('Display sub forum list'), default=True)

    class Meta:
        abstract = True
        ordering = ['tree_id', 'lft']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        app_label = 'forum'

    def __unicode__(self):
        return '{}'.format(self.name)

    @property
    def margin_level(self):
        """
        Used in templates or menus to create an easy-to-see left margin to contrast
        a forum from their parents.
        """
        return self.level * 2

    def clean(self):
        if self.parent:
            if self.parent.type == FORUM_TYPES.forum_link:
                raise ValidationError(_('A forum can not have a link forum as parent'))

        super(AbstractForum, self).clean()

    def update_trackers(self):
        self.real_topics_count = self.topics.count()
        self.topics_count = self.topics.filter(approved=True).count()
        # Compute the forum level posts count
        posts_count = sum(topic.posts_count for topic in self.topics.all())
        self.posts_count = posts_count
        self.save()
