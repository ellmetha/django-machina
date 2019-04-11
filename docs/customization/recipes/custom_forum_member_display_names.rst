#######################################
Using custom forum member display names
#######################################

Django-machina uses the standard ``User.get_username()`` method (see `here <https://docs.djangoproject.com/en/2.1/ref/contrib/auth/#django.contrib.auth.models.User.get_username>`_)
whenever it has to display forum member user names through the forums. This behaviour can be easily
changed to anything you want by setting the ``MACHINA_USER_DISPLAY_NAME_METHOD`` setting to another
method available on your project's ``User`` model. That said if your logic to generate user display
names is not defined on your project's ``User`` model, you can still customize forum member display
names. To do so you'll have to override the ``forum_member`` application and define a new
``forum_member.shortcuts.get_forum_member_display_name`` shortcut function. This is a very simple
function that takes a single user instance as input and that returns the corresponding display name.

As an example, let's say we want to display the users' full names instead of raw usernames using
an hypothetical ``get_user_full_name`` function.

The first thing to do is to override the ``forum_member`` application using the steps described in
:doc:`../overriding_applications`. Once this is done, you can create a ``shortcuts.py`` file in your
local ``forum_member`` application and defines a ``get_forum_member_display_name`` function in it.
As stated before, this function should take a single user model instance as input and return the
appropriate display name:

.. code-block:: python

    def get_forum_member_display_name(user):
        """ Given a specific user, returns their related display name. """
        return get_user_full_name(user)

Once the above function is defined, django-machina's templates will automatically use it to display
the names of forum members.
