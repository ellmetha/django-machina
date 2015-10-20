Example projects
================

*Django-machina* provides two example projects:

* a "vanilla" project which contains a standard installation of *django-machina* without customization
* a "demo" project which showcases the customization possibilities of *django-machina* (templates, logic, etc)

The vanilla project
-------------------

The "vanilla" project contains a minimum installation of *django-machina* where no customizations have been made. The project uses the default forum settings and can be usefull for discovering *django-machina*'s functionnalities.

To run this project locally, you can follow these instructions:

.. code-block:: bash

  $ git clone https://github.com/ellmetha/django-machina
  $ cd django-machina
  $ mkvirtualenv machina_vanilla_project
  (machina_vanilla_project) $ make install && pip install -r example_projects/vanilla/requirements.txt
  (machina_vanilla_project) $ cd example_projects/vanilla/src/
  (machina_vanilla_project) $ python manage.py migrate
  (machina_vanilla_project) $ python manage.py createsuperuser
  (machina_vanilla_project) $ python manage.py loaddata fixtures/*
  (machina_vanilla_project) $ python manage.py runserver

.. note::

	The previous steps assume you have `Virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_ installed on your system.

The demo project
----------------

The "demo" project aims to show the possibilities of *django-machina* in terms of personalization and customization. It showcases how *django-machina* can be used to integrate a forum into a Django project. Some of the customisations that are included in this "demo" project are listed bellow:

* a material design theme
* the use of `django-ckeditor <https://github.com/django-ckeditor/django-ckeditor/>`_ instead of `django-markdown <https://github.com/klen/django_markdown/>`_

To run this project locally, you can follow these instructions:

.. code-block:: bash

  $ git clone https://github.com/ellmetha/django-machina
  $ cd django-machina
  $ mkvirtualenv machina_demo_project
  (machina_demo_project) $ make install && pip install -r example_projects/demo/requirements.txt
  (machina_demo_project) $ cd example_projects/demo/src/
  (machina_demo_project) $ python manage.py migrate
  (machina_demo_project) $ python manage.py createsuperuser
  (machina_demo_project) $ python manage.py loaddata fixtures/*
  (machina_demo_project) $ python manage.py runserver
