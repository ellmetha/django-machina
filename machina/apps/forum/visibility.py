"""
    The visibility module
    =====================

    This module provides helper classes to manage and compute values that should be displayed when
    considering a tree of forums. This includes post counts, topic counts, siblings, ...

"""

from django.db.models.query import QuerySet
from django.utils.functional import cached_property


class ForumVisibilityContentTree:
    """ Represents a tree of ``ForumVisibilityContentNode`` instances.

    Such a tree can be used to easily compute sums or "global" values associated with a given set of
    forum instances. It can be useful to display forum information to a user (eg. in a list of
    forums, etc.).

    """

    def __init__(self, nodes=None):
        # The "nodes" argument should contain a list of ForumVisibilityContentNode instances. It
        # should be a list of all the nodes contained in the considered tree (regardless their
        # position in the tree of forum).
        self.nodes = nodes or []

    def __bool__(self):
        return len(self.forums) > 0

    @classmethod
    def from_forums(cls, forums):
        """ Initializes a ``ForumVisibilityContentTree`` instance from a list of forums. """
        root_level = None
        current_path = []
        nodes = []

        # Ensures forums last posts and related poster relations are "followed" for better
        # performance (only if we're considering a queryset).
        forums = (
            forums.select_related('last_post', 'last_post__poster')
            if isinstance(forums, QuerySet) else forums
        )

        for forum in forums:
            level = forum.level

            # Set the root level to the top node level at the first iteration.
            if root_level is None:
                root_level = level

            # Initializes a visibility forum node associated with current forum instance.
            vcontent_node = ForumVisibilityContentNode(forum)

            # Computes a relative level associated to the node.
            relative_level = level - root_level
            vcontent_node.relative_level = relative_level

            # All children nodes will be stored in an array attached to the current node.
            vcontent_node.children = []

            # Removes the forum that are not in the current branch.
            while len(current_path) > relative_level:
                current_path.pop(-1)

            if level != root_level:
                # Update the parent of the current forum.
                parent_node = current_path[-1]
                vcontent_node.parent = parent_node
                parent_node.children.append(vcontent_node)

            # Sets visible flag if applicable. The visible flag is used to determine whether a forum
            # can be seen in a forum list or not. A forum can be seen if one of the following
            # statements is true:
            #
            # * the forum is a direct child of the starting forum for the considered level
            # * the forum have a parent which is a category and this category is a direct child of
            #   the starting forum
            # * the forum have its 'display_sub_forum_list' option set to True and have a parent
            #   which is another forum. The latter is a direct child of the starting forum
            # * the forum have its 'display_sub_forum_list' option set to True and have a parent
            #   which is another forum. The later have a parent which is a category and this
            #   category is a direct child of the starting forum
            #
            # If forums at the root level don't have parents, the visible forums are those that can
            # be seen from the root of the forums tree.
            vcontent_node.visible = (
                (relative_level == 0) or
                (forum.display_sub_forum_list and relative_level == 1) or
                (forum.is_category and relative_level == 1) or
                (
                    relative_level == 2 and
                    vcontent_node.parent.parent.obj.is_category and
                    vcontent_node.parent.obj.is_forum
                )
            )

            # Add the current forum to the end of the current branch and inserts the node inside the
            # final node dictionary.
            current_path.append(vcontent_node)
            nodes.append(vcontent_node)

        tree = cls(nodes=nodes)
        for node in tree.nodes:
            node.tree = tree

        return tree

    @cached_property
    def as_dict(self):
        """ Returns a dictionary of forum ID / related node. """
        return {n.obj.id: n for n in self.nodes}

    @cached_property
    def forums(self):
        """ Returns a list of ``Forum`` instances associated with the underlying nodes. """
        return [n.obj for n in self.nodes]

    @cached_property
    def root_level(self):
        """ Returns the root level of the considered tree. """
        return self.top_nodes[0].level if self.top_nodes else None

    @cached_property
    def top_nodes(self):
        """ Returns only the node without immediate parent. """
        return list(filter(lambda n: not n.relative_level, self.nodes))

    @cached_property
    def visible_forums(self):
        """ Returns only the forum instances associated with the current tree. """
        return [n.obj for n in self.visible_nodes]

    @cached_property
    def visible_nodes(self):
        """ Returns only the visible nodes associated with the current tree. """
        return list(filter(lambda n: n.visible, self.nodes))


class ForumVisibilityContentNode:
    """ Represents a forum object and its "visibility content".

    This class provides common properties that should help computing values such as posts counts or
    topics counts for a specific forum instance.
    """

    def __init__(self, obj):
        self.obj = obj
        self.level = obj.level
        self.relative_level = None
        self.parent = None
        self.children = []
        self.tree = None
        self.visible = False

    @cached_property
    def last_post(self):
        """ Returns the latest post associated with the node or one of its descendants. """
        posts = [n.last_post for n in self.children if n.last_post is not None]
        children_last_post = max(posts, key=lambda p: p.created) if posts else None
        if children_last_post and self.obj.last_post_id:
            return max(self.obj.last_post, children_last_post, key=lambda p: p.created)
        return children_last_post or self.obj.last_post

    @cached_property
    def last_post_on(self):
        """ Returns the latest post date associated with the node or one of its descendants. """
        dates = [n.last_post_on for n in self.children if n.last_post_on is not None]
        children_last_post_on = max(dates) if dates else None
        if children_last_post_on and self.obj.last_post_on:
            return max(self.obj.last_post_on, children_last_post_on)
        return children_last_post_on or self.obj.last_post_on

    @cached_property
    def next_sibling(self):
        """ Returns the next sibling of the current node.

        The next sibling is searched in the parent node if we are not considering a top-level node.
        Otherwise it is searched inside the list of nodes (which should be sorted by tree ID) that
        is associated with the considered tree instance.
        """
        if self.parent:
            nodes = self.parent.children
            index = nodes.index(self)
            sibling = nodes[index + 1] if index < len(nodes) - 1 else None
        else:
            nodes = self.tree.nodes
            index = nodes.index(self)
            sibling = (
                next((n for n in nodes[index + 1:] if n.level == self.level), None)
                if index < len(nodes) - 1 else None
            )
        return sibling

    @cached_property
    def posts_count(self):
        """ Returns the number of posts associated with the current node and its descendants. """
        return self.obj.direct_posts_count + sum(n.posts_count for n in self.children)

    @cached_property
    def previous_sibling(self):
        """ Returns the previous sibling of the current node.

        The previous sibling is searched in the parent node if we are not considering a top-level
        node. Otherwise it is searched inside the list of nodes (which should be sorted by tree ID)
        that is associated with the considered tree instance.
        """
        if self.parent:
            nodes = self.parent.children
            index = nodes.index(self)
            sibling = nodes[index - 1] if index > 0 else None
        else:
            nodes = self.tree.nodes
            index = nodes.index(self)
            sibling = (
                next((n for n in reversed(nodes[:index]) if n.level == self.level), None)
                if index > 0 else None
            )
        return sibling

    @cached_property
    def topics_count(self):
        """ Returns the number of topics associated with the current node and its descendants. """
        return self.obj.direct_topics_count + sum(n.topics_count for n in self.children)
