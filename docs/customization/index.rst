#############
Customization
#############



*Django-machina* was built with customization in mind. The module provides useful tools to make your forum compatible with your own business logic.

Settings
--------

As most Django applications do, *django-machina* allows you to customize your forum application with a set of settings (please refer to :doc:`../settings`). *Django-machina* settings cover many aspects of your forum: markup language, pagination, images, default permissions, etc.

Templates and static files
--------------------------

If you wish to personalize the look and feel of your forum you can take advantage of the Django's template loading system. Thus you can easily override forum layouts and styles if Django is configured to look in your project first for templates before using the *django-machina*' templates.

For example, you can easily override *django-machina*' templates by configuring the ``TEMPLATE_DIRS`` setting as follows::

  TEMPLATE_DIRS = (
    PROJECT_PATH.child('src', 'vanilla_project', 'templates'),
    MACHINA_MAIN_TEMPLATE_DIR,
  )

Advanced customization mechanisms
---------------------------------

*Django-machina* relies on a dynamic class loading system that allows to override or extend many classes: class-based views, forms, models, etc.
