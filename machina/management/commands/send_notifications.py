# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from machina.apps.forum_member.utils import send_notifications


class Command(BaseCommand):
    help = 'Send email to users that have turned on notifications for subscribed topics.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            dest='interval',
            default=300,  # 5 minutes
            type=int,
            help=('Subscribers on posts created within this interval (in seconds) will '
                  'receive notifications on email.'),
        )

    def handle(self, *args, **options):
        """
        Send email to users that have turned on notifications for subscribed topics.
        """

        translation.activate(settings.LANGUAGE_CODE)
        send_notifications(options['interval'])
        translation.deactivate()
