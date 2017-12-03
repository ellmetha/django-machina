##############################
Contributing to django-machina
##############################

Here are some simple rules to help you contribute to *django-machina*. You can contribute in many
ways!

Contributing code
=================

The preferred way to contribute to *django-machina* is to submit pull requests to the
`project's Github repository <https://github.com/ellmetha/django-machina>`_. Here are some general
tips regarding pull requests.

.. warning::

    Keep in mind that you should propose new features on the
    `project's issue tracker <https://github.com/ellmetha/django-machina/issues>`_ before starting
    working on your ideas! Remember that the central aim of *django-machina* is to provide a solid
    core of a forum project - without much of extra functionality included!

Development environment
-----------------------

.. note::

    The following steps assumes you have `Pipenv <https://docs.pipenv.org/>`_ and
    `npm <https://www.npmjs.com/>`_ installed on your system.

You should first fork the
`django-machina's repository <https://github.com/ellmetha/django-machina>`_. Then you can get a
working copy of the project using the following commands:

.. code-block:: bash

    $ git clone git@github.com:<username>/django-machina.git
    $ cd django-machina
    $ make && npm install

Coding style
------------

Please make sure that your code is compliant with the
`PEP8 style guide <https://www.python.org/dev/peps/pep-0008/>`_. You can ignore the "Maximum Line
Length" requirement but the length of your lines should not exceed 100 characters. Remember that
your code will be checked using `flake8 <https://pypi.python.org/pypi/flake8>`_ and
`isort <https://github.com/timothycrosley/isort>`_. You can use the following command to trigger
such quality assurance checks:

.. code-block:: bash

    $ make qa

Tests
-----

You should not submit pull requests without providing tests. *Django-machina* uses
`pytest <http://pytest.org/latest/>`_ as a test runner but also as a syntax for tests instead of
unittest. So you should write your tests using `pytest <http://pytest.org/latest/>`_ instead of
unittest and you should not use the built-in ``django.test.TestCase``.

You can run the whole test suite using the following command:

.. code-block:: bash

    $ pipenv run py.test

Code coverage should not decrease with pull requests! You can easily get the code coverage of the
project using the following command:

.. code-block:: bash

    $ make coverage

Contributing translations
=========================

The translation work on *django-machina* is done using
`Transifex <https://www.transifex.com/django-machina-team/django-machina/>`_. Don't hesitate to
apply for a language if you want to improve the internationalization of the project.

Using the issue tracker
=======================

You should use the `project's issue tracker <https://github.com/ellmetha/django-machina/issues>`_ if
you've found a bug or if you want to propose a new feature. Don't forget to include as many details
as possible in your tickets (eg. tracebacks if this is appropriate).

Security
========

If you've found a security issue please **do not open a Github issue**. Instead, send an email at
``security@machina-forum.io``. We'll then investigate together to resolve the problem so we can make
an announcement about a solution along with the vulnerability.
