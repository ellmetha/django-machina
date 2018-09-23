#############################
Using a custom avatar backend
#############################

Django-machina has a built-in avatar system to get you started, but if your site uses a different
avatar provider, you can modify django-machina to use that.

The first thing we must do is tell django-machina to ignore the built-in avatar system:

.. code-block:: python

  MACHINA_PROFILE_AVATARS_ENABLED = False

This will hide the avatar upload field from the user's account page so they don't upload the avatar
to the wrong backend.

Now we have to modify the partial template ``partials/avatar.html`` to use our avatar provider. The
template is passed the following two parameters:

- ``profile`` - A ``ForumProfile`` instance for the user (use ``profile.user`` to get the Django
  ``User``)
- ``show_placeholder`` - A boolean telling the template whether or not to show a placeholder for
  users without an avatar

Example: using django-avatar
----------------------------

Here is an example template for
`django-avatar <https://github.com/grantmcconnaughey/django-avatar>`_:

.. code-block:: html

    {% load avatar_tags %}
    {% if profile.user|has_avatar %}
        <img class="avatar" src="{% avatar_url profile.user 260 %}" alt="{{ profile.user.username }}" />
    {% elif show_placeholder %}
        <span class="avatar empty">
          <i class="far fa-user fa-4x" ></i>
        </span>
    {% endif %}
