Getting started
===============

Requirements
------------

* `Python`_ 2.7, 3.3 or 3.4
* `Django`_ 1.4.x, 1.5.x, 1.6.x or 1.7.x
* `Pillow`_ 2.2. or higher
* `Django-model-utils`_ 2.0. or higher
* `Django-mptt`_ 0.6.1. or higher
* `Django-guardian`_ 1.2. or higher
* `Django-haystack`_ 2.1. or higher
* `Django-markdown`_ 0.7. or higher
* `Django-compressor`_ 1.4. or higher
* `Django-bootstrap3`_ 3.0. or higher
* `South`_ 1.0.1 or higher if you are using Django < 1.7


.. warning:: While *django-machina* is compatible with Django 1.5.x, this version of Django
             is no longer supported by the Django team. Please upgrade to
             Django 1.6.x or 1.7.x immediately.

.. note::

	*Django-machina* uses Markdown (*django-markdown*) by default as a syntax for forum messages, but you can change this
	in your settings.

	*Django-machina*'s default templates use *django-compressor* to handle static files and *django-bootstrap3* to render
	forms. These packages are optional and you can override this by using your own templates.

.. _Python: https://www.python.org
.. _Django: https://www.djangoproject.com
.. _Pillow: http://python-pillow.github.io/
.. _Django-model-utils: https://github.com/carljm/django-model-utils
.. _Django-mptt: https://github.com/django-mptt/django-mptt
.. _Django-guardian: https://github.com/lukaszb/django-guardian
.. _Django-haystack: https://github.com/django-haystack/django-haystack
.. _Django-markdown: https://github.com/klen/django_markdown
.. _Django-compressor: https://github.com/django-compressor/django-compressor
.. _Django-bootstrap3: https://github.com/dyve/django-bootstrap3
.. _South: http://south.aeracode.org/

Installation
------------

Install *django-machina* using::

  pip install git+git://github.com/ellmetha/django-machina.git

.. note::

	Please remember that *django-machina* is still in heavy development. It is not yet suitable for production environments.

Configuration and setup
-----------------------

First update your ``INSTALLED_APPS`` in your project's settings module. Modify it to be a list and append the *django-machina*'s  apps to this list::

  from machina import get_vanilla_apps

  INSTALLED_APS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # ...
  ] + get_vanilla_apps()
