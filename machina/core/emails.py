# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.mail import EmailMultiAlternatives
from django.template import loader

from machina.conf import settings


class BaseEmail(object):
    subject_template = ''
    html_template = ''
    text_template = ''
    from_email = None
    context = None

    @property
    def html(self):
        return self.render_template_content(self.html_template)

    @property
    def plain_text(self):
        return self.render_template_content(self.text_template)

    @property
    def subject(self):
        content = self.render_template_content(self.subject_template)
        # The subject might contain newlines etc. so strip and combine it
        # into one line.
        return ' '.join(content.splitlines()).strip()

    def __init__(self, from_email=None):
        self.from_email = from_email or settings.MACHINA_DEFAULT_FROM_EMAIL

        assert self.from_email, 'DEFAULT_FROM_EMAIL in settings is missing.'

    def get_context_data(self, **kwargs):
        """
        Return context to be in use for rendering templates.
        """
        context = {}
        context.update(**kwargs)
        return context

    def render_template_content(self, template_name):
        """
        Render content for the email template with context.
        """
        return loader.get_template(template_name).render(
            self.get_context_data(**self.context))

    def send(self, to_emails, context=None, fail_silently=True):
        """
        Send the email.
        """
        if not self.context:
            self.context = {}

        if context:
            self.context.update(context)

        msg = EmailMultiAlternatives(
            self.subject,
            self.plain_text,
            self.from_email,
            to_emails,
        )

        if self.html_template:
            msg.attach_alternative(self.html, "text/html")

        msg.send(fail_silently=fail_silently)
