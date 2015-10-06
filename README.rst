django-machina
##############

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
* ...

.. image:: https://raw.githubusercontent.com/ellmetha/django-machina/master/docs/images/machina_forum_header.png
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

Authors
=======

Morgan Aubert (@ellmetha) <morgan.aubert@zoho.com> and contributors_

.. _contributors: https://github.com/ellmetha/django-machina/contributors

License
=======

BSD. See ``LICENSE`` for more details.
