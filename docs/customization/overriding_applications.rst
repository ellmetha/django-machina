#########################
Overriding an application
#########################

*Django-machina* relies on a dynamic class-loading system that allows you to override or extend many aspects of its applications. The *django-machina* applications are listed below:

+-------------------------------+----------------------------------------------------------------------------------------------------+
| Application name              | Definition                                                                                         |
+===============================+====================================================================================================+
| **forum**                     | This application provides the ability to browse a tree of forums                                   |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_conversation**        | This application handles all the conversations that can happen in forums                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_feeds**               | This application allows to get forum topics as RSS feeds                                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_member**              | This application provides functionalities to forum members                                         |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_moderation**          | This application provides moderation tools to moderators                                           |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_permission**          | This application provides the proper tools to allow permission checks on forums                    |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_search**              | This application allows to search within forums                                                    |
+-------------------------------+----------------------------------------------------------------------------------------------------+
| **forum_tracking**            | This application allows to determine which forums or topics have been read by a given user         |
+-------------------------------+----------------------------------------------------------------------------------------------------+

.. note::

    Overriding these applications is not a trivial task. Most of the time you will need to dig into the source code of *django-machina* in order to discover how things were implemented. This will allow you to find exactly which method should be rewritten in order to achieve the task at hand.
