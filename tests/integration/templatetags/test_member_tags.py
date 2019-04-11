import pytest

from machina.templatetags.forum_member_tags import forum_member_display_name
from machina.test.factories import UserFactory


@pytest.mark.django_db
class TestForumMemberDisplayNameFilter:
    def test_returns_the_display_name_of_a_specific_user(self):
        user = UserFactory.create()
        assert forum_member_display_name(user) == user.username
