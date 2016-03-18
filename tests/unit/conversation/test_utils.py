# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import RequestFactory
from faker import Factory as FakerFactory
import pytest

from machina.apps.forum_conversation.utils import get_client_ip

faker = FakerFactory.create()


@pytest.mark.django_db
class TestIpAddressExtractor(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()

    def test_can_determine_the_ip_address_with_the_http_x_forwarded_for_header(self):
        # Setup
        request = self.factory.get('/')
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = faker.ipv4()
        request.META = parameters
        # Run
        ip_address = get_client_ip(request)
        # Check
        assert ip_address == parameters['HTTP_X_FORWARDED_FOR']

    def test_can_determine_the_ip_address_with_the_remote_addr_header(self):
        # Setup
        request = self.factory.get('/')
        parameters = request.META.copy()
        parameters['HTTP_X_FORWARDED_FOR'] = None
        parameters['REMOTE_ADDR'] = faker.ipv4()
        request.META = parameters
        # Run
        ip_address = get_client_ip(request)
        # Check
        assert ip_address == parameters['REMOTE_ADDR']
