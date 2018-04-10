from django import template
from django.contrib.auth.models import User
from machina.conf.settings import FORUM_USER_DISPLAY

register = template.Library()

@register.simple_tag
def get_username(user_id):
    user=User.objects.get(pk=user_id)
    if FORUM_USER_DISPLAY:
        user = template.Context(dict(user=user))
        t = template.Template(FORUM_USER_DISPLAY)
        return t.render(user)
    else:
        return user.username
