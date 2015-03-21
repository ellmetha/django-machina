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
