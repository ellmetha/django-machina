###################################
Customization underlying mechanisms
###################################

Django-machina relies on a dynamic class-loading system that allows you to override or extend many
aspects of its applications. The underlying mechanisms are directly inspired from the class loading
system provided by the django-oscar_ e-commerce framework.

.. _django-oscar: https://github.com/django-oscar/django-oscar

If you look through django-machina's codebase, you'll find that most of the classes or functions are
imported using this kind of statement:

.. code-block:: python

  from machina.core.loading import get_class
  PostForm = get_class('forum_conversation.forms', 'PostForm')

The ``get_class`` function is provided by the ``machina.core.loading`` module. It is used instead of
standard import statements such as ``from machina.forum_conversation.forms import PostForm``.

The ``get_class`` function imports a single class from a specified module. It takes two arguments:
the first one is the label of the module from which you want to import your class (eg.
``forum_conversations.forms``) ; the second-one is the name of the class to import. The
``get_class`` function works as follow:

* it will look through your Machina overridden applications in order to find an application that
  matches the application name included in the module label
* it will try to load the class from the specified module if it exists
* if the specified module is not present in the overriden application or if the class cannot be
  retrieved from the custom module, the class will be imported from the default Machina application

.. note::

    The ``get_class`` function can only import customized classes from applications that have been
    properly overridden. Please head over to :doc:`overriding_applications` for more details on how
    to override a django-machina application.

So the ``get_class`` function allows you to define local versions of Machina classes in order to
customize your forum behaviors. Most of the time you will create a subclass of a specific class in
order to customize the way it behaves. For example you could extend the
``forum_conversation.views.TopicView`` in order to add some data to the context:

::

  from machina.apps.forum_conversation.views import TopicView as BaseTopicView

  class TopicView(BaseTopicView):
    def get_context_data(self, **kwargs):
      context = super(TopicView, self).get_context_data(**kwargs)
      # Some additional data can be added to the context here
      context['foo'] = 'bar'
      return context

If this view is part of an overridden application, django-machina will use it instead of the default
``TopicView``.

So this dynamic class-loading system allows to make changes to the django-machina's core
functionalities by altering only the classes whose behavior must be updated to achieve the task at
hand.
