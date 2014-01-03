# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.core.urlresolvers import reverse
from django.core.urlresolvers import NoReverseMatch

# Local application / specific library imports


class AdminClientMixin(object):
    """
    Mixin that can be used to append a test to WebClientTestCase in order to
    test that the admin base views associated with a given model are accessible
    and so avoid some boilerplate code.
    It is assumed to be used with a WebClientTestCase subclass.
    """
    is_staff = True
    model = None

    def test_has_accessible_base_views(self):
        model = self.model
        urls = (
            'admin:{}_{}_changelist',
            'admin:{}_{}_add',
        )
        urls = [raw_url.format(model._meta.app_label, model._meta.module_name) for raw_url in urls]
        try:
            for raw_url in urls:
                url = reverse(raw_url)
                response = self.client.get(url, follow=True)
                self.assertIsOk(response)
        except NoReverseMatch:
            self.fail('At least one admin base views is not available for the following model: {}'.format(model))
