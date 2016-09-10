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

  $ npm install -g less
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

	The previous steps assumes you have `Virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_ installed on your system.

If you have `Docker <https://www.docker.com/>`_ and `Docker Compose <https://docs.docker.com/compose/>`_ installed on your system you can also run the "vanilla" project using the following commands:

.. code-block:: bash

  $ git clone https://github.com/ellmetha/django-machina
  $ docker-compose build vanilla
  $ docker-compose up vanilla

In that case you can navigate to http://localhost:8082 to test the project.

The demo project
----------------

The "demo" project aims to show the possibilities of *django-machina* in terms of personalization and customization. It showcases how *django-machina* can be used to integrate a forum into a Django project. Some of the customisations that are included in this "demo" project are listed bellow:

* a new theme
* the use of `django-ckeditor <https://github.com/django-ckeditor/django-ckeditor/>`_ instead of the default Markdown editor

To run this project locally, you can follow these instructions:

.. code-block:: bash

  $ npm install -g lesss
  $ git clone https://github.com/ellmetha/django-machina
  $ cd django-machina
  $ mkvirtualenv machina_demo_project
  (machina_demo_project) $ make install && pip install -r example_projects/demo/requirements.txt
  (machina_demo_project) $ cd example_projects/demo/src/
  (machina_demo_project) $ python manage.py migrate
  (machina_demo_project) $ python manage.py createsuperuser
  (machina_demo_project) $ python manage.py loaddata fixtures/*
  (machina_demo_project) $ python manage.py runserver

If you have `Docker <https://www.docker.com/>`_ and `Docker Compose <https://docs.docker.com/compose/>`_ installed on your system you can also run the "demo" project using the following commands:

.. code-block:: bash

  $ git clone https://github.com/ellmetha/django-machina
  $ docker-compose build demo
  $ docker-compose up demo

In that case you can navigate to http://localhost:8081 to test the project.
