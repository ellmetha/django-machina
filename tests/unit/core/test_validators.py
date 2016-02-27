# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from faker import Factory as FakerFactory
import pytest

from machina.core import validators

faker = FakerFactory.create()


class TestNullableMaxLengthValidator(object):
    def test_can_prevent_validation_if_the_limit_value_is_none(self):
        # Setup
        validator_1 = validators.NullableMaxLengthValidator(None)
        validator_2 = validators.NullableMaxLengthValidator(3)
        # Run & check
        assert validator_1(faker.text()) is None
        with pytest.raises(ValidationError):
            validator_2('test' * 10)
