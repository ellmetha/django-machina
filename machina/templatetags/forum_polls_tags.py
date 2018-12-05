from django import template

from machina.core.db.models import get_model
from machina.core.loading import get_class


TopicPollVote = get_model('forum_polls', 'TopicPollVote')

get_anonymous_user_forum_key = get_class(
    'forum_permission.shortcuts', 'get_anonymous_user_forum_key',
)

register = template.Library()


@register.filter
def has_been_completed_by(poll, user):
    """ This will return a boolean indicating if the passed user has already voted in the given
        poll.

    Usage::
        {% if poll|has_been_completed_by:user %}...{% endif %}

    """
    user_votes = TopicPollVote.objects.filter(
        poll_option__poll=poll)
    if user.is_anonymous:
        forum_key = get_anonymous_user_forum_key(user)
        user_votes = user_votes.filter(anonymous_key=forum_key) if forum_key \
            else user_votes.none()
    else:
        user_votes = user_votes.filter(voter=user)
    return user_votes.exists()
