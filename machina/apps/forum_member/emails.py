# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.core.emails import BaseEmail


class NotificationEmail(BaseEmail):
    """
    Notification email sent to users that subscribe on a topic.
    """
    subject_template = 'forum_member/emails/notification.subject.txt'
    html_template = 'forum_member/emails/notification.html'
    text_template = 'forum_member/emails/notification.txt'
