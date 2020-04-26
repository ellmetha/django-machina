Example project
===============

Django-machina provides an example project containing a standard installation of the module without
any customizations.

This project uses the default forum settings and can be usefull for discovering django-machina's
functionalities.

To run this project locally, you can follow these instructions:

.. code-block:: bash

  $ git clone https://github.com/ellmetha/django-machina
  $ cd django-machina
  $ make
  $ cd example_project/
  $ make migrate
  $ make superuser
  $ poetry run python manage.py loaddata project/fixtures/*
  $ make server

.. note::

    The previous steps assumes you have `Poetry <https://python-poetry.org/>`_ installed on your
    system.
