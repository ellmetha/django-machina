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
* Moderation and pre-modaration
* ...

.. image:: https://raw.githubusercontent.com/ellmetha/django-machina/master/docs/_images/machina_forum_header.png
  :target: http://django-machina.readthedocs.org/en/latest/

|

*Django-machina* was built with integration in mind: the application is designed to be used inside existing Django applications. It is not a standalone forum solution.

*Django-machina* was built with customization and extensibility in mind: each single functionality of the application can be customized or overriden to accommodate with your needs. In fact, *django-machina* uses the same techniques as those introduced by the famous django-oscar_ e-commerce framework to allow powerfull customizations.

.. _django-oscar: https://github.com/django-oscar/django-oscar

.. contents::

Requirements
============

Python 2.7+ or 3.3+, Django 1.5+. Please refer to the requirements_ section of the documentation for a full list of dependencies.

.. _requirements: http://django-machina.readthedocs.org/en/latest/getting_started.html#requirements

Documentation
=============

Head over to the `documentation <http://django-machina.readthedocs.org/en/>`_ for all the details on how to set up your forum and how to customize it to suit your needs.

What still needs to be done
===========================

* Documenting the customization features provided by django-machina and some common use cases. These features are similar to the ones provided by the django-oscar_ e-commerce framework
* Documenting the ways to contribute to *django-machina*
* Implementing the topic subscription feature : a user can get a list of all topics to which he subscribed
* Implementing a way to allow or disallow posts edition for anonymous users by using a random key stored in the session

Authors
=======

Morgan Aubert (@ellmetha) <morgan.aubert@zoho.com> and contributors_

.. _contributors: https://github.com/ellmetha/django-machina/contributors

License
=======

BSD. See ``LICENSE`` for more details.
