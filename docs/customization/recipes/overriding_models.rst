#############################
Overriding application models
#############################

Django-machina allows you to override its models. This can be useful if you want to add new methods
or new fields to existing django-machina models.

To illustrate this functionality, we will add an ``icon`` field to the ``Topic`` model (which is
part of the ``forum_conversation`` app) in order to allow users select an icon for the topics they
create.

Prerequisite
------------

Please ensure that you have correctly followed the instructions described in
:doc:`../overriding_applications` before trying to override django-machina models. If so, you should
have created a Python package with the same application label as the app you want to override. This
new application should be defined in your ``INSTALLED_APPS`` setting.

Most importantly, you should've created a ``models.py`` file inside your package in order to
reference the models of the overriden application:

.. code-block:: python

  # Custom models should be declared before importing
  # django-machina models

  from machina.apps.forum_conversation.models import *  # noqa

Finally you should have copied the content of the ``migration`` folder from the application you want
to override into your own local application.

Defining a new custom model
---------------------------

In order to define a new version of an existing django-machina model you have to define a new class
that subclasses the abstract model class of the model you want to override. The new model you define
must have the exact same name as the model you are trying to override.

For example, in order to define a custom version of the ``Topic`` model it is necessary to subclass
the ``machina.apps.forum_conversation.abstract_models.AbstractTopic`` abstract model:

.. code-block:: python

  from django.db import models
  from machina.apps.forum_conversation.abstract_models import AbstractTopic

  # Custom models should be declared before importing
  # django-machina models

  class Topic(AbstractTopic):
      icon = models.ImageField(verbose_name="Icon", upload_to="forum/topic_icons")

  from machina.apps.forum_conversation.models import *  # noqa

.. note::

    You need to ensure that the import of django-machina's models is always done at the bottom of
    your ``models.py`` file. This is very important in the event that you define overridden models
    because it will ensure that your overriden models will be loaded by Django instead of the
    original versions provided by django-machina.

Creating migrations
-------------------

As stated previously, you should've copied the content of the ``migration`` folder from the
application you want to override into your own local application. Then you just have to create a new
migration related to the changes you made to the overriden models:

.. code-block:: bash

  $ django-admin makemigrations forum_conversation
