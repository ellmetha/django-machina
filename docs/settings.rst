########
Settings
########

This is a comprehensive list of all the settings *django-machina* provides. All settings are optional.

General
*******

``MACHINA_FORUM_NAME``
----------------------

Default: ``'Machina'``

The forum name.

``MACHINA_MARKUP_LANGUAGE``
---------------------------

Default: ``('django_markdown.utils.markdown', {})``

This setting defines how posts content is translated into HTML on the forum. It must be a two-tuple. The first element should be a string corresponding to the Python dotted path to a function returning HTML from a content expressed in a markup language. The second element of the tuple is a dictionary of keyword arguments to pass to the latest function (the dictionary should be empty if the function does not require any argument).

*Django-machina* uses Markdown as the default syntax for forum messages.

``MACHINA_MARKUP_WIDGET``
-------------------------

Default: ``'django_markdown.widgets.MarkdownWidget'``

This setting defines the widget used inside topic and post forms. It should be a Python dotted path to a Django form widget.

Forum
*****

``MACHINA_FORUM_IMAGE_UPLOAD_TO``
---------------------------------

Default: ``'machina/forum_images'``

The media subdirectory where forum images should be uploaded.

``MACHINA_FORUM_IMAGE_WIDTH``
-----------------------------

Default: ``None``

The width used to create the thumbnail that is displayed for each forum that has an image in the list of forums.

``MACHINA_FORUM_IMAGE_HEIGHT``
------------------------------

Default: ``None``

The height used to create the thumbnail that is displayed for each forum that has an image in the list of forums.

``MACHINA_FORUM_TOPICS_NUMBER_PER_PAGE``
----------------------------------------

Default: ``20``

The number of topics displayed inside one page of a forum.

Conversation
************

``MACHINA_TOPIC_ANSWER_SUBJECT_PREFIX``
---------------------------------------

Default: ``'Re:'``

This is the prefix used to pre-populate the subject of a topic reply. For example: if a reply is being posted for the *Lorem Ipsum* topic, the prefilled subject will be *Re: Lorem Ipsum* in the reply form.

``MACHINA_TOPIC_POSTS_NUMBER_PER_PAGE``
---------------------------------------

Default: ``15``

The number of posts displayed inside one page of a forum topic.

``MACHINA_TOPIC_REVIEW_POSTS_NUMBER``
-------------------------------------

Default: ``10``

The number of posts displayed when posting a reply. The posts displayed are related to the considered forum topic.

Polls
*****

``MACHINA_POLL_MAX_OPTIONS_PER_USER``
-------------------------------------

Default: ``10``

This setting defines the maximum number of poll options that can be selected by users when voting. Note that this setting does not impact the users who vote in a poll but only the poll creator. The latest has to choose the number of poll options allowed per user, and this value cannot exceed the value of this setting.

Attachments
***********

``MACHINA_ATTACHMENT_FILE_UPLOAD_TO``
-------------------------------------

Default: ``'machina/attachments'``

The media subdirectory where forum attachments should be uploaded.

``MACHINA_ATTACHMENT_CACHE_NAME``
---------------------------------

Default: ``'machina_attachments'``

The name of the cache used to store temporary post attachments.

Member
******

``MACHINA_PROFILE_AVATAR_UPLOAD_TO``
------------------------------------

Default: ``'machina/avatar_images'``


The media subdirectory where forum member avatars should be uploaded.

``MACHINA_PROFILE_AVATAR_WIDTH``
--------------------------------

Default: ``None``

The imposed avatar width for forum member profiles.

``MACHINA_PROFILE_AVATAR_HEIGHT``
---------------------------------

Default: ``None``

The imposed avatar height for forum member profiles.

``MACHINA_PROFILE_AVATAR_MIN_WIDTH``
------------------------------------

Default: ``None``

The imposed avatar minimum width for forum member profiles.

``MACHINA_PROFILE_AVATAR_MIN_HEIGHT``
-------------------------------------

Default: ``None``

The imposed avatar minimum height for forum member profiles.

``MACHINA_PROFILE_AVATAR_MAX_WIDTH``
------------------------------------

Default: ``None``

The imposed avatar maximum width for forum member profiles.

``MACHINA_PROFILE_AVATAR_MAX_HEIGHT``
-------------------------------------

Default: ``None``

The imposed avatar maximum height for forum member profiles.

``MACHINA_PROFILE_AVATAR_MAX_UPLOAD_SIZE``
------------------------------------------

Default: ``0``

The maximum avatar size for forum member profiles. A value of ``0`` means that there is no size limitation.

``MACHINA_PROFILE_SIGNATURE_MAX_LENGTH``
----------------------------------------

Default: ``255``

The maximum number of characters that can be used in a member signature.

Permission
**********

``MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS``
--------------------------------------------------------

Default: ``[]``

*Django-machina* relies on a permission system based on per-forum permissions. This allows you to define which permissions should be applied for each forum, for each user and for each group of users. However you might want to not have to deal with complex permissions and grant the same basic permissions to all the users and for all the forums you created. In that case, this setting can be used in order to define which permissions should be granted to all authenticated users. Note that the permissions specified in this list are granted only if the considered forum does not have any permission for the considered authenticated user. For example, the setting could be specified as follows::

	MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = [
	    'can_see_forum',
	    'can_read_forum',
	    'can_start_new_topics',
	    'can_reply_to_topics',
	    'can_edit_own_posts',
	    'can_post_without_approval',
	    'can_create_polls',
	    'can_vote_in_polls',
	    'can_download_file',
	]

For a full list of the available forum permissions, please refer to :doc:`forum_permissions`.
