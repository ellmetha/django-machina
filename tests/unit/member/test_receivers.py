import pytest

from machina.core.db.models import get_model
from machina.test.factories import PostFactory, UserFactory, create_forum, create_topic


ForumProfile = get_model('forum_member', 'ForumProfile')


@pytest.mark.django_db
class TestIncreasePostsCountReceiver(object):
    def test_can_increase_the_posts_count_of_the_post_being_created(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        PostFactory.create(topic=topic, poster=u1, approved=True)
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count + 1

    def test_cannot_increase_the_posts_count_of_the_post_being_created_if_it_is_not_approved(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        PostFactory.create(topic=topic, poster=u1, approved=False)
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count

    def test_can_increase_the_posts_count_of_a_post_being_approved(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        post = PostFactory.create(topic=topic, poster=u1, approved=False)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        post.approved = True
        post.save()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count + 1

    def test_do_nothing_if_the_poster_is_anonymous(self):
        # Setup
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=None)
        # Run
        PostFactory.create(topic=topic, poster=None, username='test')
        # Check
        assert ForumProfile.objects.exists() is False


@pytest.mark.django_db
class TestDecreasePostsCountAfterPostUnaprovalReceiver(object):
    def test_can_decrease_the_posts_count_of_a_post_being_set_as_not_approved(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        profile = ForumProfile.objects.get(user=u1)
        post = PostFactory.create(topic=topic, poster=u1, approved=True)
        # Run
        post.approved = False
        post.save()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == 1


@pytest.mark.django_db
class TestDecreasePostsCountAfterPostDeletionReceiver(object):
    def test_can_decrease_the_posts_count_of_the_post_being_deleted(self):
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        post = PostFactory.create(topic=topic, poster=u1)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        post.delete()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count - 1

    def test_do_nothing_if_the_poster_is_anonymous(self):
        # Setup
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=None)
        post = PostFactory.create(topic=topic, poster=None, username='test')
        # Run
        post.delete()
        # Check
        assert ForumProfile.objects.exists() is False

    def test_do_nothing_if_the_post_is_not_approved(self):
        # Setup
        # Setup
        u1 = UserFactory.create()
        top_level_forum = create_forum()
        topic = create_topic(forum=top_level_forum, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        PostFactory.create(topic=topic, poster=u1)
        post = PostFactory.create(topic=topic, poster=u1, approved=False)
        profile = ForumProfile.objects.get(user=u1)
        initial_posts_count = profile.posts_count
        # Run
        post.delete()
        # Check
        profile.refresh_from_db()
        assert profile.posts_count == initial_posts_count
