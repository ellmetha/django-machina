#############################################
Using another markup language for forum posts
#############################################

.. _django-ckeditor: https://github.com/django-ckeditor/django-ckeditor

Django-machina uses Markdown as the default syntax for forum messages, which is provided by the use
of a built-in widget using the
`EasyMDE Markdown editor <https://github.com/Ionaru/easy-markdown-editor>`_. But you can easily
change this in your settings. We will see how to do this.

It should be noted that django-machina relies on specific model fields to store forum messages.
These fields contribute two columns to the model where they are used: the first one is used to store
any content written by using a markup language (eg. BBCode or Markdown) and the second one keeps the
rendered content obtained by converting the initial content to HTML. Thus forum messages are stored
in two versions: plain and HTML.

Example: using django-ckeditor
------------------------------

Let's use django-ckeditor_ instead of the default widget in order to benefit from a powerful wysiwyg
editor.

The first thing to do is to add ``ckeditor`` in our ``INSTALLED_APPS`` setting:

.. code-block:: python

  INSTALLED_APS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Machina related apps:
    'mptt',
    'haystack',
    'widget_tweaks',
    'ckeditor',

    # Machina apps:
    'machina',
    'machina.apps.forum',
    'machina.apps.forum_conversation',
    'machina.apps.forum_conversation.forum_attachments',
    'machina.apps.forum_conversation.forum_polls',
    'machina.apps.forum_feeds',
    'machina.apps.forum_moderation',
    'machina.apps.forum_search',
    'machina.apps.forum_tracking',
    'machina.apps.forum_member',
    'machina.apps.forum_permission',
  )

Then we must set the ``MACHINA_MARKUP_LANGUAGE`` and ``MACHINA_MARKUP_WIDGET`` settings in order to
tell django-machina the widget to use when displaying forms:

.. code-block:: python

  MACHINA_MARKUP_LANGUAGE = None
  MACHINA_MARKUP_WIDGET = 'ckeditor.widgets.CKEditorWidget'

When using a wysiwyg editor such as CKEditor we do not use a specific markup language because we
directly get the content in HTML. This is why the ``MACHINA_MARKUP_LANGUAGE`` setting is set to
``None``. The ``MACHINA_MARKUP_WIDGET`` indicates the Python dotted path to the CKEditor form
widget.

The last thing to do is to ensure that you use the required assets in your templates. Basically, you
have to ensure that the media property is used in your form templates (this is the case if you have
not modified the default topic/post templates):

.. code-block:: html

  {% block css %}
    {{ block.super }}
    {{ post_form.media.css }}
  {% endblock css %}

  {% block js %}
    {{ block.super }}
    {{ post_form.media.js }}
  {% endblock js %}
