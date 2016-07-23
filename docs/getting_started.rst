Getting started
===============

Requirements
------------

* `Python`_ 2.7, 3.3, 3.4 or 3.5
* `Django`_ 1.8.x or 1.9.x
* `Pillow`_ 2.2. or higher
* `Django-mptt`_ 0.8. or higher
* `Django-haystack`_ 2.1. or higher
* `Django-pagedown`_ 0.1. or higher
* `Markdown`_ 2.6. or higher
* `Django-widget-tweaks`_ 1.4. or higher


.. note::

	*Django-machina* uses Markdown by default as a syntax for forum messages, but you can change this
	in your settings.

.. _Python: https://www.python.org
.. _Django: https://www.djangoproject.com
.. _Pillow: http://python-pillow.github.io/
.. _Django-mptt: https://github.com/django-mptt/django-mptt
.. _Django-haystack: https://github.com/django-haystack/django-haystack
.. _Django-pagedown: https://github.com/timmyomahony/django-pagedown
.. _Markdown: https://github.com/waylan/Python-Markdown
.. _Django-widget-tweaks: https://github.com/kmike/django-widget-tweaks

Installation
------------

Install *django-machina* using::

  pip install django-machina

Project configuration
---------------------

Django settings
~~~~~~~~~~~~~~~

First update your ``INSTALLED_APPS`` in your project's settings module. Modify it to be a list and append the *django-machina*'s  apps to this list::

  from machina import get_apps as get_machina_apps

  INSTALLED_APS = [
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
    'pagedown',
  ] + get_machina_apps()

.. note::

  As previously stated, Markdown is the default syntax used for forum messages.

*Django-machina* uses *django-mptt* to handle the tree of forum instances. Search capabilities are provided by *django-haystack*.

Then update your ``TEMPLATE_CONTEXT_PROCESSORS`` setting as follows::

  TEMPLATE_CONTEXT_PROCESSORS = (
    # ...
    # Machina
    'machina.core.context_processors.metadata',
  )

Add the ``machina.apps.forum_permission.middleware.ForumPermissionMiddleware`` to your ``MIDDLEWARE_CLASSES`` setting::

  MIDDLEWARE_CLASSES = (
      # ...
      # Machina
      'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
  )

Edit your ``TEMPLATE_DIRS`` setting so that it includes the *django-machina*'s template directory::

  from machina import MACHINA_MAIN_TEMPLATE_DIR

  TEMPLATE_DIRS = (
    # ...
    MACHINA_MAIN_TEMPLATE_DIR,
  )

Edit your ``STATICFILES_DIRS`` setting so that it includes the *django-machina*'s static directory::

  from machina import MACHINA_MAIN_STATIC_DIR

  STATICFILES_DIRS = (
    # ...
    MACHINA_MAIN_STATIC_DIR,
  )

Finally you have to add a new cache to your settings. This cache will be used to store temporary post attachments. Note that this ``machina_attachments`` cache must use the ``django.core.cache.backends.filebased.FileBasedCache`` backend, as follows::

  CACHES = {
    'default': {
      'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
      'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
      'LOCATION': '/tmp',
    }
  }

Django-haystack settings
~~~~~~~~~~~~~~~~~~~~~~~~

*Django-machina* uses *django-haystack* to provide search for forum conversations. *Django-haystack* allows you to plug in many search backends so you may want to choose the one that best suits your need.

You can start using the basic search provided by the *django-haystack*'s simple backend::

  HAYSTACK_CONNECTIONS = {
    'default': {
      'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
  }

You can also decide to use a more powerfull backend such as *Solr* or *Whoosh*::

  HAYSTACK_CONNECTIONS = {
    'default': {
      'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
      'PATH': os.path.join(PROJECT_PATH, 'whoosh_index'),
    },
  }

Database and migrations
-----------------------

Just use the ``migrate`` command to install the models::

  python manage.py migrate

URLs configuration
------------------

Finally you have to update your main ``urls.py`` module in order to include the forum's URLs::

  from machina.app import board

  urlpatterns = patterns(
    # [...]

    # Apps
    url(r'^forum/', include(board.urls)),
  )

Creating your first forums
--------------------------

You can now navigate to http://127.0.0.1:8000/forum/ in order to visualize the index of your forum board. As you should see no forum have been created yet. *Django-machina* does not ship with pre-created forums, so you should navigate to your administration panel and create some forum instances.

.. note::

  A common practice when creating forums is to embed them in categories in order to better organize the tree of forum instances. Please refer to :doc:`glossary` if you do not know what a category is in a forum tree.

*Congrats! You're in.*
