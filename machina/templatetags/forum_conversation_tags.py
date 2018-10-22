from django import template

from machina.conf import settings as machina_settings


register = template.Library()


@register.filter
def posted_by(post, user):
    """ This will return a boolean indicating if the passed user has posted the given forum post.

    Usage::

        {% if post|posted_by:user %}...{% endif %}

    """
    return post.poster == user


@register.inclusion_tag('forum_conversation/topic_pages_inline_list.html')
def topic_pages_inline_list(topic):
    """ This will render an inline pagination for the posts related to the given topic.

    Usage::

        {% topic_pages_inline_list my_topic %}

    """
    data_dict = {
        'topic': topic,
    }

    pages_number = ((topic.posts_count - 1) // machina_settings.TOPIC_POSTS_NUMBER_PER_PAGE) + 1
    if pages_number > 5:
        data_dict['first_pages'] = range(1, 5)
        data_dict['last_page'] = pages_number
    elif pages_number > 1:
        data_dict['first_pages'] = range(1, pages_number + 1)

    return data_dict
