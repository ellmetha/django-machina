#############
Customization
#############



Django-machina was built with customization in mind. The module provides useful tools to make your
forum compatible with your own business logic.

Settings
--------

As most Django applications do, django-machina allows you to customize your forum application with a
set of settings (please refer to :doc:`../settings`). Django-machina's settings cover many aspects
of your forum: markup language, pagination, images, default permissions, etc.

Templates and static files
--------------------------

If you wish to personalize the look and feel of your forum you can take advantage of the Django's
template loading system. Thus you can easily override forum layouts and styles if Django is
configured to look in your project first for templates before using the django-machina's templates.

For example, you can easily override django-machina's templates by configuring your template
directories as follows in your ``TEMPLATES`` setting::

  import os

  TEMPLATES = [
    {
      'BACKEND': 'django.template.backends.django.DjangoTemplates',
      'DIRS': [
        os.path.join(PROJECT_PATH, 'myproject/templates'),
        MACHINA_MAIN_TEMPLATE_DIR,
      ],
      'OPTIONS': {
        'context_processors': [
          # [...]
        ],
      },
    },
  ]

Advanced customization mechanisms
---------------------------------

Django-machina relies on a dynamic class loading system that allows to override or extend its Python
classes: class-based views, forms, models, etc. This gives you the power to adapt your forum to your
own business logic.

In order to benefit from this dynamic class loading system, you will need to override a
django-machina application. Please head over to the following topics in order to achieve this:

.. toctree::
    :maxdepth: 1

    overriding_applications
    underlying_mechanisms

Recipes
-------

Here is a list of simple guides demonstrating how to solve common customization problems when using
django-machina:

.. toctree::
    :maxdepth: 1

    recipes/overriding_models
    recipes/using_another_markup_language
    recipes/custom_avatar_backend
