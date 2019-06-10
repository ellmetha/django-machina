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
  $ pipenv run python manage.py migrate
  $ pipenv run python manage.py createsuperuser
  $ pipenv run python manage.py loaddata project/fixtures/*
  $ pipenv run python manage.py runserver

.. note::

    The previous steps assumes you have `Pipenv <https://docs.pipenv.org/>`_ installed on your
    system.
