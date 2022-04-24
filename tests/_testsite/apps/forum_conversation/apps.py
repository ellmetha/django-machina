from machina.apps.forum_conversation.apps import ForumConversationAppConfig \
    as BaseForumConversationAppConfig


class ForumConversationAppConfig(BaseForumConversationAppConfig):
    default = True
    name = 'tests._testsite.apps.forum_conversation'
