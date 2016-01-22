django-machina
##############

.. image:: https://readthedocs.org/projects/django-machina/badge/?style=flat-square&version=latest
   :target: http://django-machina.readthedocs.org/en/latest/
   :alt: Documentation Status

.. image:: http://img.shields.io/travis/ellmetha/django-machina.svg?style=flat-square
    :target: http://travis-ci.org/ellmetha/django-machina
    :alt: Build status

.. image:: http://img.shields.io/coveralls/ellmetha/django-machina.svg?style=flat-square
    :target: https://coveralls.io/r/ellmetha/django-machina
    :alt: Coveralls status

|

**This application is in heavy development. It is not yet suitable for production environments.**

*Django-machina* is a forum framework for Django providing a way to build community-driven websites. It offers a full-featured yet very extensible forum solution:

* Topic and post editing
* Forums tree management
* Per-forum permissions
* Anonymous posting
* Polls and attachments
* Moderation and pre-moderation
* ...

.. image:: https://raw.githubusercontent.com/ellmetha/django-machina/master/docs/_images/machina_forum_header.png
  :target: http://django-machina.readthedocs.org/en/latest/

|

*Django-machina* was built with integration in mind: the application is designed to be used inside existing Django applications. It is not a standalone forum solution.

*Django-machina* was built with customization and extensibility in mind: each single functionality of the application can be customized or overriden to accommodate with your needs. In fact, *django-machina* uses the same techniques as those introduced by the famous django-oscar_ e-commerce framework to allow powerfull customizations.

.. _django-oscar: https://github.com/django-oscar/django-oscar

.. contents::

Documentation
=============

Online browsable documentation is available at https://django-machina.readthedocs.org.

Head over to the documentation for all the details on how to set up your forum and how to customize it to suit your needs.

Requirements
============

Python 2.7+ or 3.3+, Django 1.7+. Please refer to the requirements_ section of the documentation for a full list of dependencies.

.. _requirements: https://django-machina.readthedocs.org/en/latest/getting_started.html#requirements

Roadmap
=======

* Topic subscriptions: a user can get a list of all topics to which he subscribed
* A view to get all the posts of a forum member
* Display a list of last post in users' profiles

Authors
=======

Morgan Aubert (@ellmetha) and contributors_

.. _contributors: https://github.com/ellmetha/django-machina/contributors

License
=======

BSD. See ``LICENSE`` for more details.
