# -*- coding: utf-8 -*-

from django.core import validators


class NullableMaxLengthValidator(validators.MaxLengthValidator):
    """ Provides a way to not validate an input if the max length is None """
    def __call__(self, value):
        if self.limit_value is None:
            # If the limit value is None, this means that there is no
            # limit value at all. The default validation process is not
            # performed.
            return
        super(NullableMaxLengthValidator, self).__call__(value)
