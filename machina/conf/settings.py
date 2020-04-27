"""
    Django-machina settings
    =======================

    This module define the settings of the django-machina forum framework. Each setting can be
    overriden in the Django project's settings. These settings allow to customize many aspects of
    the forum application, such as conversations, polls, permissions, members, ...

"""

from django.conf import settings


# General
FORUM_NAME = getattr(settings, 'MACHINA_FORUM_NAME', 'Machina')
MARKUP_LANGUAGE = getattr(
    settings, 'MACHINA_MARKUP_LANGUAGE',
    ('machina.core.markdown.markdown', {'safe_mode': True, 'extras': {'break-on-newline': True}})
)
MARKUP_WIDGET = getattr(
    settings, 'MACHINA_MARKUP_WIDGET', 'machina.forms.widgets.MarkdownTextareaWidget'
)
MARKUP_WIDGET_KWARGS = getattr(settings, 'MACHINA_MARKUP_WIDGET_KWARGS', {})

MARKUP_MAX_LENGTH_VALIDATOR = getattr(
    settings, 'MACHINA_MARKUP_MAX_LENGTH_VALIDATOR',
    'machina.core.validators.NullableMaxLengthValidator'
)

BASE_TEMPLATE_NAME = getattr(settings, 'MACHINA_BASE_TEMPLATE_NAME', '_base.html')
USER_DISPLAY_NAME_METHOD = getattr(
    settings,
    'MACHINA_USER_DISPLAY_NAME_METHOD',
    'get_username',
)

# Forum
FORUM_IMAGE_UPLOAD_TO = getattr(settings, 'MACHINA_FORUM_IMAGE_UPLOAD_TO', 'machina/forum_images')
FORUM_IMAGE_WIDTH = getattr(settings, 'MACHINA_FORUM_IMAGE_WIDTH', 100)
FORUM_IMAGE_HEIGHT = getattr(settings, 'MACHINA_FORUM_IMAGE_HEIGHT', 70)

DEFAULT_FORUM_IMAGE_SETTINGS = {
    'width': FORUM_IMAGE_WIDTH,
    'height': FORUM_IMAGE_HEIGHT
}

FORUM_TOPICS_NUMBER_PER_PAGE = getattr(settings, 'MACHINA_FORUM_TOPICS_NUMBER_PER_PAGE', 20)


# Conversation
TOPIC_ANSWER_SUBJECT_PREFIX = getattr(settings, 'MACHINA_TOPIC_ANSWER_SUBJECT_PREFIX', 'Re:')
POST_CONTENT_MAX_LENGTH = getattr(settings, 'MACHINA_POST_CONTENT_MAX_LENGTH', None)

TOPIC_POSTS_NUMBER_PER_PAGE = getattr(settings, 'MACHINA_TOPIC_POSTS_NUMBER_PER_PAGE', 15)
TOPIC_REVIEW_POSTS_NUMBER = getattr(settings, 'MACHINA_TOPIC_REVIEW_POSTS_NUMBER', 10)


# Polls
POLL_MAX_OPTIONS_PER_POLL = getattr(settings, 'MACHINA_POLL_MAX_OPTIONS_PER_POLL', 30)
POLL_MAX_OPTIONS_PER_USER = getattr(settings, 'MACHINA_POLL_MAX_OPTIONS_PER_USER', 10)


# Attachments
ATTACHMENT_FILE_UPLOAD_TO = getattr(
    settings, 'MACHINA_ATTACHMENT_FILE_UPLOAD_TO', 'machina/attachments'
)
ATTACHMENT_CACHE_NAME = getattr(settings, 'MACHINA_ATTACHMENT_CACHE_NAME', 'machina_attachments')
ATTACHMENT_MAX_FILES_PER_POST = getattr(settings, 'MACHINA_ATTACHMENT_MAX_FILES_PER_POST', 15)

# Member
PROFILE_AVATAR_UPLOAD_TO = getattr(
    settings, 'MACHINA_PROFILE_AVATAR_UPLOAD_TO', 'machina/avatar_images'
)

PROFILE_AVATARS_ENABLED = getattr(settings, 'MACHINA_PROFILE_AVATARS_ENABLED', True)
PROFILE_AVATAR_WIDTH = getattr(settings, 'MACHINA_PROFILE_AVATAR_WIDTH', 150)
PROFILE_AVATAR_HEIGHT = getattr(settings, 'MACHINA_PROFILE_AVATAR_HEIGHT', 250)
PROFILE_AVATAR_MIN_WIDTH = getattr(settings, 'MACHINA_PROFILE_AVATAR_MIN_WIDTH', None)
PROFILE_AVATAR_MAX_WIDTH = getattr(settings, 'MACHINA_PROFILE_AVATAR_MAX_WIDTH', None)
PROFILE_AVATAR_MIN_HEIGHT = getattr(settings, 'MACHINA_PROFILE_AVATAR_MIN_HEIGHT', None)
PROFILE_AVATAR_MAX_HEIGHT = getattr(settings, 'MACHINA_PROFILE_AVATAR_MAX_HEIGHT', None)
PROFILE_AVATAR_MAX_UPLOAD_SIZE = getattr(settings, 'MACHINA_PROFILE_AVATAR_MAX_UPLOAD_SIZE', 0)

DEFAULT_AVATAR_SETTINGS = {
    'width': PROFILE_AVATAR_WIDTH,
    'height': PROFILE_AVATAR_HEIGHT,
    'min_width': PROFILE_AVATAR_MIN_WIDTH,
    'max_width': PROFILE_AVATAR_MAX_WIDTH,
    'min_height': PROFILE_AVATAR_MIN_HEIGHT,
    'max_height': PROFILE_AVATAR_MAX_HEIGHT,
    'max_upload_size': PROFILE_AVATAR_MAX_UPLOAD_SIZE
}

PROFILE_SIGNATURE_MAX_LENGTH = getattr(settings, 'MACHINA_PROFILE_SIGNATURE_MAX_LENGTH', 255)

PROFILE_RECENT_POSTS_NUMBER = getattr(settings, 'MACHINA_PROFILE_RECENT_POSTS_NUMBER', 15)
PROFILE_POSTS_NUMBER_PER_PAGE = getattr(settings, 'MACHINA_PROFILE_POSTS_NUMBER_PER_PAGE', 15)


# Permission
DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = getattr(
    settings, 'MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS', []
)
