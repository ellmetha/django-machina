# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe

from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model('forum', 'Forum')

PermissionHandler = get_class('forum_permission.handler', 'PermissionHandler')
TrackingHandler = get_class('forum_tracking.handler', 'TrackingHandler')

register = template.Library()


class RecurseTreeForumVisibilityContentNode(template.Node):
    def __init__(self, template_nodes, forums_contents_var):
        self.template_nodes = template_nodes
        self.forums_contents_var = forums_contents_var

    def _render_node(self, context, node):
        bits = []
        context.push()
        for child in node.children:
            bits.append(self._render_node(context, child))
        context['node'] = node
        context['children'] = mark_safe(''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        forums_contents = self.forums_contents_var.resolve(context)
        roots = forums_contents.top_nodes
        bits = [self._render_node(context, node) for node in roots]
        return ''.join(bits)


@register.tag
def recurseforumcontents(parser, token):
    """ Iterates over the content nodes and renders the contained forum block for each node. """
    bits = token.contents.split()
    forums_contents_var = template.Variable(bits[1])

    template_nodes = parser.parse(('endrecurseforumcontents',))
    parser.delete_first_token()

    return RecurseTreeForumVisibilityContentNode(template_nodes, forums_contents_var)


@register.inclusion_tag('forum/forum_list.html', takes_context=True)
def forum_list(context, forum_visibility_contents):
    """ Renders the considered forum list.

    This will render the given list of forums by respecting the order and the depth of each
    forum in the forums tree.

    Usage::

        {% forum_list my_forums %}

    """
    request = context.get('request')
    tracking_handler = TrackingHandler(request=request)

    data_dict = {
        'forum_contents': forum_visibility_contents,
        'unread_forums': tracking_handler.get_unread_forums_from_list(
            request.user, forum_visibility_contents.forums),
        'user': request.user,
        'request': request,
    }

    root_level = forum_visibility_contents.root_level
    if root_level is not None:
        data_dict['root_level'] = root_level
        data_dict['root_level_middle'] = root_level + 1
        data_dict['root_level_sub'] = root_level + 2

    return data_dict
