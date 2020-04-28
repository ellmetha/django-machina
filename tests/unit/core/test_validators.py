from importlib import reload

import pytest
from django.core.exceptions import ImproperlyConfigured, ValidationError
from faker import Faker

from machina.conf import settings as machina_settings
from machina.core import validators


faker = Faker()


class TestNullableMaxLengthValidator(object):
    def test_can_prevent_validation_if_the_limit_value_is_none(self):
        # Setup
        validator_1 = validators.NullableMaxLengthValidator(None)
        validator_2 = validators.NullableMaxLengthValidator(3)
        # Run & check
        assert validator_1(faker.text()) is None
        with pytest.raises(ValidationError):
            validator_2('test' * 10)


class TestMarkupMaxLengthValidator(object):
    def test_default_validator(self):
        # Setup
        validator = validators.MarkupMaxLengthValidator(None)
        # Run & check
        assert validator(faker.text()) is None

    def test_custom_validator(self):
        # Setup
        machina_settings.MARKUP_MAX_LENGTH_VALIDATOR = 'django.core.validators.MaxLengthValidator'
        validator = validators.MarkupMaxLengthValidator(2)
        # Run & check
        assert validator('aa') is None
        with pytest.raises(ValidationError):
            validator('aaa')

    def test_should_not_allow_non_accessible_validator(self):
        # Setup
        machina_settings.MARKUP_MAX_LENGTH_VALIDATOR = 'it.will.fail.Validator'
        # Run & check
        with pytest.raises(ImproperlyConfigured):
            reload(validators)
        del machina_settings.MARKUP_MAX_LENGTH_VALIDATOR
        with pytest.raises(ImproperlyConfigured):
            reload(validators)
