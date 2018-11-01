import pytest

from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories import (
    PostFactory, UserFactory, create_category_forum, create_forum, create_topic
)


Forum = get_model('forum', 'Forum')

ForumVisibilityContentTree = get_class('forum.visibility', 'ForumVisibilityContentTree')


@pytest.mark.django_db
class TestForumVisibilityContentTree(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = UserFactory.create()

        # Set up the following forum tree:
        #
        #     top_level_cat
        #         forum_1
        #         forum_2
        #             forum_2_child_1
        #     top_level_forum_1
        #     top_level_forum_2
        #         sub_cat
        #             sub_sub_forum
        #     top_level_forum_3
        #         forum_3
        #             forum_3_child_1
        #                 forum_3_child_1_1
        #                     deep_forum
        #     last_forum
        #
        self.top_level_cat = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)

        self.top_level_forum_1 = create_forum()

        self.top_level_forum_2 = create_forum()
        self.sub_cat = create_category_forum(parent=self.top_level_forum_2)
        self.sub_sub_forum = create_forum(parent=self.sub_cat)

        self.top_level_forum_3 = create_forum()
        self.forum_3 = create_forum(parent=self.top_level_forum_3)
        self.forum_3_child_1 = create_forum(parent=self.forum_3)
        self.forum_3_child_1_1 = create_forum(parent=self.forum_3_child_1)
        self.deep_forum = create_forum(parent=self.forum_3_child_1_1)

        self.last_forum = create_forum()

        # Set up a topic and some posts
        self.topic_1 = create_topic(forum=self.forum_1, poster=self.user)
        self.post_1 = PostFactory.create(topic=self.topic_1, poster=self.user)
        self.topic_2 = create_topic(forum=self.forum_2, poster=self.user)
        self.post_2 = PostFactory.create(topic=self.topic_2, poster=self.user)
        self.topic_3 = create_topic(forum=self.forum_2_child_1, poster=self.user)
        self.post_3 = PostFactory.create(topic=self.topic_3, poster=self.user)

    def test_can_be_initialized_from_a_list_of_forums(self):
        # Run & check
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        for forum in Forum.objects.all():
            assert forum in visibility_tree.forums

    def test_can_return_the_root_level_number(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.root_level == 0

    def test_can_return_its_top_nodes(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert [n.obj for n in visibility_tree.top_nodes] == [
            self.top_level_cat, self.top_level_forum_1, self.top_level_forum_2,
            self.top_level_forum_3, self.last_forum, ]

    def test_can_return_its_visible_forums(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert [n.obj for n in visibility_tree.visible_nodes] == [
            self.top_level_cat, self.forum_1, self.forum_2, self.forum_2_child_1,
            self.top_level_forum_1, self.top_level_forum_2, self.sub_cat, self.top_level_forum_3,
            self.forum_3, self.last_forum, ]
        assert visibility_tree.visible_forums == [
            self.top_level_cat, self.forum_1, self.forum_2, self.forum_2_child_1,
            self.top_level_forum_1, self.top_level_forum_2, self.sub_cat, self.top_level_forum_3,
            self.forum_3, self.last_forum, ]


@pytest.mark.django_db
class TestForumVisibilityContentNode(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user = UserFactory.create()

        # Set up the following forum tree:
        #
        #     top_level_cat
        #         forum_1
        #         forum_2
        #             forum_2_child_1
        #     top_level_forum_1
        #     top_level_forum_2
        #         sub_cat
        #             sub_sub_forum
        #     top_level_forum_3
        #         forum_3
        #             forum_3_child_1
        #                 forum_3_child_1_1
        #                     deep_forum
        #     last_forum
        #
        self.top_level_cat = create_category_forum()

        self.forum_1 = create_forum(parent=self.top_level_cat)
        self.forum_2 = create_forum(parent=self.top_level_cat)
        self.forum_2_child_1 = create_forum(parent=self.forum_2)

        self.top_level_forum_1 = create_forum()

        self.top_level_forum_2 = create_forum()
        self.sub_cat = create_category_forum(parent=self.top_level_forum_2)
        self.sub_sub_forum = create_forum(parent=self.sub_cat)

        self.top_level_forum_3 = create_forum()
        self.forum_3 = create_forum(parent=self.top_level_forum_3)
        self.forum_3_child_1 = create_forum(parent=self.forum_3)
        self.forum_3_child_1_1 = create_forum(parent=self.forum_3_child_1)
        self.deep_forum = create_forum(parent=self.forum_3_child_1_1)

        self.last_forum = create_forum()

        # Set up a topic and some posts
        self.topic_1 = create_topic(forum=self.forum_1, poster=self.user)
        self.post_1 = PostFactory.create(topic=self.topic_1, poster=self.user)
        self.topic_2 = create_topic(forum=self.forum_2, poster=self.user)
        self.post_2 = PostFactory.create(topic=self.topic_2, poster=self.user)
        self.topic_3 = create_topic(forum=self.forum_2_child_1, poster=self.user)
        self.post_3 = PostFactory.create(topic=self.topic_3, poster=self.user)

    def test_can_return_its_last_post(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.top_level_cat.id].last_post == self.post_3

    def test_can_return_its_last_post_date(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.top_level_cat.id].last_post_on == self.post_3.created

    def test_can_return_its_next_sibiling(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.forum_1.id].next_sibling \
            == visibility_tree.as_dict[self.forum_2.id]
        assert visibility_tree.as_dict[self.top_level_cat.id].next_sibling \
            == visibility_tree.as_dict[self.top_level_forum_1.id]
        assert visibility_tree.as_dict[self.forum_3_child_1_1.id].next_sibling is None

    def test_can_return_its_previous_sibiling(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.forum_2.id].previous_sibling \
            == visibility_tree.as_dict[self.forum_1.id]
        assert visibility_tree.as_dict[self.top_level_forum_1.id].previous_sibling \
            == visibility_tree.as_dict[self.top_level_cat.id]
        assert visibility_tree.as_dict[self.forum_3_child_1_1.id].previous_sibling is None

    def test_can_return_its_post_count(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.top_level_cat.id].posts_count == 3

    def test_can_return_its_topic_count(self):
        # Setup
        visibility_tree = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        # Run & check
        assert visibility_tree.as_dict[self.top_level_cat.id].topics_count == 3

    def test_can_return_an_appropriate_boolean_value(self):
        visibility_tree_1 = ForumVisibilityContentTree.from_forums(Forum.objects.all())
        visibility_tree_2 = ForumVisibilityContentTree.from_forums(
            self.last_forum.get_descendants()
        )
        assert visibility_tree_1
        assert not visibility_tree_2
