import pytest

from machina.core.loading import get_class
from machina.test.factories import UserFactory


get_forum_member_display_name = get_class('forum_member.shortcuts', 'get_forum_member_display_name')


@pytest.mark.django_db
class TestGetForumMemberDisplayNameShortcut:
    def test_returns_the_display_name_of_a_specific_user(self):
        user = UserFactory.create()
        assert get_forum_member_display_name(user) == user.username
