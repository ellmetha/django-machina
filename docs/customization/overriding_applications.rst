#########################
Overriding an application
#########################

*Django-machina* relies on a dynamic class-loading system that allows you to override or extend many aspects of its applications. The *django-machina* applications are listed below:

+-------------------------------+----------------------------------------------------------------------------------------------------+
| Application name              | Definition                                                                                         |
+===============================+====================================================================================================+
| **forum**                     | This application provides the ability to browse a tree of forums                                   |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_conversation**        | This application handles all the conversations that can happen in forums                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_feeds**               | This application allows to get forum topics as RSS feeds                                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_member**              | This application provides functionalities to forum members                                         |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_moderation**          | This application provides moderation tools to moderators                                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_permission**          | This application provides the proper tools to allow permission checks on forums                    |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_search**              | This application allows to search within forums                                                    |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_tracking**            | This application allows to determine which forums or topics have been read by a given user         |
+-------------------------------+----------------------------------------------------------------------------------------------------+

.. note::

    Overriding these applications is not a trivial task. Most of the time you will need to dig into the source code of *django-machina* in order to discover how things were implemented. This will allow you to find exactly which method should be rewritten in order to achieve the task at hand.

Duplicate the application
-------------------------

Let's say we want to override the ``machina.apps.forum_conversation`` application.

Create a Python package with the same application label
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first thing to do is to create a Python package with the same application label as the app you want to override. This package can live under an ``apps`` Python package that acts as a root folder for your overridden applications, as shown below:

.. code-block:: bash

  $ mkdir -p apps/forum_conversation
  $ touch apps/__init__.py
  $ touch apps/forum_conversation/__init__.py

Import the application models if needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All *django-machina*'s applications do not necessarily contain models. So this step may be skipped depending on the application you want to override. In the other case, it is necessary to reference the models of the overridden application by creating a ``models.py`` file in your package::

  # -*- coding: utf-8 -*-

  from __future__ import unicode_literals

  # Custom models should be declared before importing
  # django-machina models

  from machina.apps.forum_conversation.models import *  # noqa

Your overridden application may need to add new models or modify *django-machina*'s own models. As stated in this snippet, custom models must be declared **before** the import of the *django-machina*'s models. This means that you can override a *django-machina* model in order to change the way it behaves if you want. Please refer to :doc:`recipes/overriding_models` to get detailed instructions on how to override *django-machina*'s models.

Only importing *django-machina*'s models is not enough. You have to ensure the models migrations can be used by your Django project. You have two possibilities to do so:

  * you can copy the content of the ``migrations`` folder from the application you want to override to your own local application
  * you can configure the ``MIGRATION_MODULES`` setting to reference the original migrations of the application you want to override

::

    MIGRATION_MODULES = {
      'forum_conversation': 'machina.apps.forum_conversation.migrations',
    }

.. note::

    The second possibility should only be used if you are sure you will not define new models or overridden models into your local application

Import the application admin classes if needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As previously stated, this step can be skipped if the application you want to override does not contain models. In the other case you will want to create an ``admin.py`` file in your package in order to reference the admin classes of the overridden application::

  # -*- coding: utf-8 -*-

  from __future__ import unicode_literals
  from machina.apps.forum_conversation.admin import *  # noqa

Define the application AppConfig
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of *django-machina*'s applications define sublclasses of Django's ``AppConfig`` which can perform initialization operations. *Django-machina* ``AppConfig`` instances are defined inside sub-modules called ``registry_config``. You need to define an ``AppConfig`` subclass for your custom application by subclassing the overridden application ``AppConfig``. So your application's ``__init__.py`` should report the custom application ``AppConfig``::

    default_app_config = 'yourproject.apps.forum_conversation.registry_config.ConversationRegistryConfig'

And in ``registry_config.py`` in you application you have something like::

    from machina.apps.forum_conversation.registry_config import ConversationRegistryConfig as BaseConversationRegistryConfig

    class ConversationRegistryConfig(BaseConversationRegistryConfig):
        name = 'yourproject.apps.forum_conversation'


Add the local application to your INSTALLED_APPS
------------------------------------------------

Finally you have to tell Django to use your overridden application instead of the *django-machina*'s original application. You can do this by adding your application as a second argument to the ``get_apps`` function in your Django settings::

  from machina import get_apps as get_machina_apps

  INSTALLED_APS = [
    # ...
  ] + get_machina_apps(['yourproject.apps.forum_conversation', ])

The list you pass to the ``get_apps`` function must contain overridden applications.
