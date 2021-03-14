import factory
import factory.django

from machina.core.db.models import get_model


ForumPermission = get_model('forum_permission', 'ForumPermission')
GroupForumPermission = get_model('forum_permission', 'GroupForumPermission')
UserForumPermission = get_model('forum_permission', 'UserForumPermission')


class ForumPermissionFactory(factory.django.DjangoModelFactory):
    codename = factory.Sequence(lambda n: 'perm-{}'.format(n))

    class Meta:
        model = ForumPermission


class UserForumPermissionFactory(factory.django.DjangoModelFactory):
    permission = factory.SubFactory(ForumPermissionFactory)

    class Meta:
        model = UserForumPermission


class GroupForumPermissionFactory(factory.django.DjangoModelFactory):
    permission = factory.SubFactory(ForumPermissionFactory)

    class Meta:
        model = GroupForumPermission
