# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from machina.conf import settings as machina_settings
from machina.core import validators
from machina.core.loading import get_class
from machina.models.abstract_models import DatedModel
from machina.models.fields import MarkupTextField


ApprovedManager = get_class('forum_conversation.managers', 'ApprovedManager')


@python_2_unicode_compatible
class AbstractTopic(DatedModel):
    """
    Represents a forum topic.
    """
    forum = models.ForeignKey(
        'forum.Forum', related_name='topics', on_delete=models.CASCADE,
        verbose_name=_('Topic forum'))
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_('Poster'), )

    # The subject of the thread should correspond to the one associated with the first post
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    slug = models.SlugField(max_length=255, verbose_name=_('Slug'))

    # Sticky, Announce, Global topic or Default topic ; that's what a topic can be
    TOPIC_POST, TOPIC_STICKY, TOPIC_ANNOUNCE = 0, 1, 2
    TYPE_CHOICES = (
        (TOPIC_POST, _('Default topic')),
        (TOPIC_STICKY, _('Sticky')),
        (TOPIC_ANNOUNCE, _('Announce')),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES, verbose_name=_('Topic type'), db_index=True)

    # A topic can be locked, unlocked or moved
    TOPIC_UNLOCKED, TOPIC_LOCKED, TOPIC_MOVED = 0, 1, 2
    STATUS_CHOICES = (
        (TOPIC_UNLOCKED, _('Topic unlocked')),
        (TOPIC_LOCKED, _('Topic locked')),
        (TOPIC_MOVED, _('Topic moved')),
    )
    status = models.PositiveIntegerField(
        choices=STATUS_CHOICES, verbose_name=_('Topic status'), db_index=True)

    # A topic can be approved before publishing ; defaults to True. The value of this flag
    # should correspond to the one associated with the first post
    approved = models.BooleanField(verbose_name=_('Approved'), default=True, db_index=True)

    # The number of posts included in this topic (only those that are approved)
    posts_count = models.PositiveIntegerField(
        verbose_name=_('Posts count'), editable=False, blank=True, default=0)

    # The number of time the topic has been viewed
    views_count = models.PositiveIntegerField(
        verbose_name=_('Views count'), editable=False, blank=True, default=0)

    # The date of the latest post
    last_post_on = models.DateTimeField(verbose_name=_('Last post added on'), blank=True, null=True)

    # The first post and the last post of the topic. The first post can be unnaproved. The last post
    # must be approved
    first_post = models.ForeignKey(
        'forum_conversation.Post', editable=False, related_name='+', blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_('First post'))
    last_post = models.ForeignKey(
        'forum_conversation.Post', editable=False, related_name='+', blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_('Last post'))

    # Many users can subscribe to this topic
    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='topic_subscriptions',
        blank=True, verbose_name=_('Subscribers'))

    objects = models.Manager()
    approved_objects = ApprovedManager()

    class Meta:
        abstract = True
        app_label = 'forum_conversation'
        ordering = ['-type', '-last_post_on', ]
        get_latest_by = 'last_post_on'
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __str__(self):
        return self.first_post.subject if self.first_post is not None else self.subject

    @property
    def is_topic(self):
        """
        Returns True if the topic is a default topic.
        """
        return self.type == self.TOPIC_POST

    @property
    def is_sticky(self):
        """
        Returns True if the topic is a sticky topic.
        """
        return self.type == self.TOPIC_STICKY

    @property
    def is_announce(self):
        """
        Returns True if the topic is an announce.
        """
        return self.type == self.TOPIC_ANNOUNCE

    @property
    def is_locked(self):
        """
        Returns True if the topic is locked.
        """
        return self.status == self.TOPIC_LOCKED

    def has_subscriber(self, user):
        """
        Returns True if the given user is a subscriber of this topic.
        """
        if not hasattr(self, '_subscribers'):
            self._subscribers = list(self.subscribers.all())
        return user in self._subscribers

    def clean(self):
        super(AbstractTopic, self).clean()
        if self.forum.is_category or self.forum.is_link:
            raise ValidationError(
                _('A topic can not be associated with a category or a link forum'))

    def save(self, *args, **kwargs):
        # It is vital to track the changes of the forum associated with a topic in order to
        # maintain counters up-to-date.
        old_instance = None
        if self.pk:
            old_instance = self.__class__._default_manager.get(pk=self.pk)

        # Update the slug field
        self.slug = slugify(force_text(self.subject), allow_unicode=True)

        # Do the save
        super(AbstractTopic, self).save(*args, **kwargs)

        # If any change has been made to the parent forum, trigger the update of the counters
        if old_instance and old_instance.forum != self.forum:
            self.update_trackers()
            # The previous parent forum counters should also be updated
            if old_instance.forum:
                old_forum = old_instance.forum
                old_forum.refresh_from_db()
                old_forum.update_trackers()

    def _simple_save(self, *args, **kwargs):
        """
        Calls the parent save method in order to avoid the checks for topic forum changes
        which can result in triggering a new update of the counters associated with the
        current topic.
        This allow the database to not be hit by such checks during very common and regular
        operations such as those provided by the update_trackers function; indeed these operations
        will never result in an update of a topic's forum.
        """
        super(AbstractTopic, self).save(*args, **kwargs)

    def delete(self, using=None):
        super(AbstractTopic, self).delete(using)
        self.forum.update_trackers()

    def update_trackers(self):
        """
        Updates the posts count, the update date and the link toward the last post
        associated with the current topic.
        """
        self.posts_count = self.posts.filter(approved=True).count()
        first_post = self.posts.all().order_by('created').first()
        last_post = self.posts.filter(approved=True).order_by('-created').first()
        self.first_post = first_post
        self.last_post = last_post
        self.last_post_on = last_post.created if last_post else None
        self._simple_save()
        # Trigger the forum-level trackers update
        self.forum.update_trackers()


@python_2_unicode_compatible
class AbstractPost(DatedModel):
    """
    Represents a forum post. A forum post is always linked to a topic.
    """
    topic = models.ForeignKey(
        'forum_conversation.Topic', related_name='posts', on_delete=models.CASCADE,
        verbose_name=_('Topic'))
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='posts',
        blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Poster'))
    poster_ip = models.GenericIPAddressField(
        verbose_name=_('Poster IP address'), blank=True, null=True, default='2002::0')
    anonymous_key = models.CharField(
        max_length=100, verbose_name=_('Anonymous user forum key'), blank=True, null=True)

    # Each post can have its own subject. The subject of the thread corresponds to the
    # one associated with the first post
    subject = models.CharField(verbose_name=_('Subject'), max_length=255)

    # Content
    content = MarkupTextField(
        verbose_name=_('Content'), validators=[validators.NullableMaxLengthValidator(
            machina_settings.POST_CONTENT_MAX_LENGTH)])

    # Username: if the user creating a topic post is not authenticated, he must enter a username
    username = models.CharField(verbose_name=_('Username'), max_length=155, blank=True, null=True)

    # A post can be approved before publishing ; defaults to True
    approved = models.BooleanField(verbose_name=_('Approved'), default=True, db_index=True)

    # The user can choose if they want to display their signature with the content of the post
    enable_signature = models.BooleanField(
        verbose_name=_('Attach a signature'), default=True, db_index=True)

    # A post can be edited for several reason (eg. moderation) ; the reason why it has been
    # updated can be specified
    update_reason = models.CharField(
        max_length=255, verbose_name=_('Update reason'), blank=True, null=True)

    # Tracking data
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, editable=False, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_('Lastly updated by'))
    updates_count = models.PositiveIntegerField(
        verbose_name=_('Updates count'), editable=False, blank=True, default=0)

    objects = models.Manager()
    approved_objects = ApprovedManager()

    class Meta:
        abstract = True
        app_label = 'forum_conversation'
        ordering = ['created', ]
        get_latest_by = 'created'
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __str__(self):
        return self.subject

    @property
    def is_topic_head(self):
        """
        Returns True if the post is the first post of the topic.
        """
        return self.topic.first_post.id == self.id if self.topic.first_post else False

    @property
    def is_topic_tail(self):
        """
        Returns True if the post is the last post of the topic.
        """
        return self.topic.last_post.id == self.id if self.topic.last_post else False

    @property
    def is_alone(self):
        """
        Returns True if the post is the only single post of the topic.
        """
        return self.topic.posts.count() == 1

    @property
    def position(self):
        """
        Returns an integer corresponding to the position of the post in the topic.
        """
        position = self.topic.posts.filter(Q(created__lt=self.created) | Q(id=self.id)).count()
        return position

    def clean(self):
        super(AbstractPost, self).clean()

        # At least a poster (user) or a session key must be associated with
        # the post.
        if self.poster is None and self.anonymous_key is None:
            raise ValidationError(
                _('A user id or an anonymous key must be associated with a post.'))
        if self.poster and self.anonymous_key:
            raise ValidationError(_('A user id or an anonymous key must be associated with a post, '
                                    'but not both.'))

        if self.anonymous_key and not self.username:
            raise ValidationError(_('A username must be specified if the poster is anonymous'))

    def save(self, *args, **kwargs):
        new_post = self.pk is None
        super(AbstractPost, self).save(*args, **kwargs)

        # Ensures that the subject of the thread corresponds to the one associated
        # with the first post. Do the same with the 'approved' flag.
        if (new_post and self.topic.first_post is None) or self.is_topic_head:
            if self.subject != self.topic.subject or self.approved != self.topic.approved:
                self.topic.subject = self.subject
                self.topic.approved = self.approved

        # Trigger the topic-level trackers update
        self.topic.update_trackers()

    def delete(self, using=None):
        if self.is_alone:
            # The default way of operating is to trigger the deletion of the associated topic
            # only if the considered post is the only post embedded in the topic
            self.topic.delete()
        else:
            super(AbstractPost, self).delete(using)
            self.topic.update_trackers()
