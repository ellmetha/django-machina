# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
# Local application / specific library imports
from machina.apps.conversation.registry_config import ConversationRegistryConfig as BaseConversationRegistryConfig


class ConversationRegistryConfig(BaseConversationRegistryConfig):
    name = 'tests._testsite.apps.conversation'
