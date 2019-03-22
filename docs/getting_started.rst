Getting started
===============

Requirements
------------

* `Python`_ 3.4, 3.5, 3.6 and 3.7
* `Django`_ 2.0.x, 2.1.x and 2.2x
* `Pillow`_ 2.2. or higher
* `Django-mptt`_ 0.8. or higher
* `Django-haystack`_ 2.1. or higher
* `Markdown2`_ 2.3. or higher
* `Django-widget-tweaks`_ 1.4. or higher

.. note::

    Django-machina uses Markdown by default as a syntax for forum messages, but you can change this
    in your settings.

.. _Python: https://www.python.org
.. _Django: https://www.djangoproject.com
.. _Pillow: http://python-pillow.github.io/
.. _Django-mptt: https://github.com/django-mptt/django-mptt
.. _Django-haystack: https://github.com/django-haystack/django-haystack
.. _Markdown2: https://github.com/trentm/python-markdown2
.. _Django-widget-tweaks: https://github.com/kmike/django-widget-tweaks

Installation
------------

Install django-machina using:

.. code-block:: console

    $ pip install django-machina

Project configuration
---------------------

Django settings
~~~~~~~~~~~~~~~

First update your ``INSTALLED_APPS`` in your project's settings module. Modify it so that it
includes the machina's dependencies and the machina's own applications as follows:

.. code-block:: python

    INSTALLED_APS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.admin',

        # Machina dependencies:
        'mptt',
        'haystack',
        'widget_tweaks',

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

.. note::

    Django-machina uses django-mptt to handle the tree of forum instances. Search capabilities are
    provided by django-haystack.

Then modify your ``TEMPLATES`` settings so that it includes the django-machina's template
directory and the extra ``metadata`` context processor:

.. code-block:: python

    from machina import MACHINA_MAIN_TEMPLATE_DIR

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': (
                # ...
                MACHINA_MAIN_TEMPLATE_DIR,
            ),
            'OPTIONS': {
                'context_processors': [
                    # ...
                    # Machina
                    'machina.core.context_processors.metadata',
                ],
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]
            },
        },
    ]

Add the ``machina.apps.forum_permission.middleware.ForumPermissionMiddleware`` to your
``MIDDLEWARE`` setting:

.. code-block:: python

    MIDDLEWARE = (
        # ...
        # Machina
        'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
    )

Edit your ``STATICFILES_DIRS`` setting so that it includes the django-machina's static directory:

.. code-block:: python

    from machina import MACHINA_MAIN_STATIC_DIR

    STATICFILES_DIRS = (
        # ...
        MACHINA_MAIN_STATIC_DIR,
    )

Finally you have to add a new cache to your settings. This cache will be used to store temporary
post attachments. Note that this ``machina_attachments`` cache must use the
``django.core.cache.backends.filebased.FileBasedCache`` backend, as follows:

.. code-block:: python

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'machina_attachments': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/tmp',
        },
    }

Django-haystack settings
~~~~~~~~~~~~~~~~~~~~~~~~

Django-machina uses django-haystack to provide search for forum conversations. Django-haystack
allows you to plug in many search backends so you may want to choose the one that best suits your
need.

You can start using the basic search provided by the django-haystack's simple backend:

.. code-block:: python

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        },
    }

You can also decide to use a more powerfull backend such as *Solr* or *Whoosh*:

.. code-block:: python

    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join(PROJECT_PATH, 'whoosh_index'),
        },
    }

.. note::

    It should be noticed that you'll have to run the ``update_index`` Haystack's command once your
    forum is properly set up in order to make your topics & posts searchable.

Database and migrations
-----------------------

Just use the ``migrate`` command to install the models:

.. code-block:: shell

    $ python manage.py migrate

URLs configuration
------------------

Finally you have to update your main ``urls.py`` module in order to include the forum's URLs:

.. code-block:: python

    from django.urls import include, path
    from machina import urls as machina_urls

    urlpatterns = [
        # [...]
        path('forum/', include(machina_urls)),
    ]

Creating your first forums
--------------------------

You can now navigate to http://127.0.0.1:8000/forum/ in order to visualize the index of your forum
board (and you can use the ``forum:index`` URL name to add a link toward the forum in your Django
templates). As you should see no forums have been created yet. Django-machina does not ship with
pre-created forums, so you should navigate to your administration panel and create some forum
instances.

.. note::

    A common practice when creating forums is to embed them in categories in order to better
    organize the tree of forum instances. Please refer to :doc:`glossary` if you do not know what a
    category is in a forum tree.

*Congrats! You're in.*
