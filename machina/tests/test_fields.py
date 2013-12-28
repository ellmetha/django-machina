# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals
try:
    from imp import reload
except ImportError:
    pass
import os

# Third party imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase
from django.utils.six import BytesIO

# Local application / specific library imports
from machina.conf import settings as machina_settings
from machina.core.compat import PILImage as Image
from machina.models import fields
from machina.tests import RESIZED_IMAGE_HEIGHT
from machina.tests import RESIZED_IMAGE_WIDTH
from machina.tests import TestableModel


class MarkupTextFieldTestCase(TestCase):
    # The following tests involve the django-precise-bbcode
    # app. This one can be used with Machina in order to
    # provide a support for the BBCode syntax. But instead
    # we can use another Django app providing support for
    # other syntax (eg. Markdown).
    MARKUP_TEXT_FIELD_TESTS = (
        ('[b]hello [u]world![/u][/b]', '<strong>hello <u>world!</u></strong>'),
        ('[url=http://google.com]goto google[/url]', '<a href="http://google.com">goto google</a>'),
        ('[b]hello [u]worlsd![/u][/b]', '<strong>hello <u>worlsd!</u></strong>'),
        ('[b]안녕하세요[/b]', '<strong>안녕하세요</strong>'),
    )

    def test_markup_text_field_accept_none_values(self):
        # Setup
        test = TestableModel()
        test.content = None
        # Run
        test.save()
        # Check
        self.assertIsNone(test.content)
        rendered = hasattr(test.content, 'rendered')
        self.assertFalse(rendered)

    def test_markup_text_field_saving(self):
        # Run & check
        for markup_text, expected_html_text in self.MARKUP_TEXT_FIELD_TESTS:
            test = TestableModel()
            test.content = markup_text
            test.save()
            self.assertEqual(test.content.rendered, expected_html_text)

    def test_markup_text_field_descriptor_protocol(self):
        # Setup
        test = TestableModel()
        test.content = '[b]hello[/b]'
        test.save()
        field = test._meta.get_field('content')
        markup_content = '[b]hello world![/b]'
        markup_content_len = len(markup_content)
        # Run
        test.content.raw = markup_content
        markup_bk = test.content
        test.content = markup_bk
        test.save()
        # Check
        self.assertEqual(field.value_to_string(test), markup_content)
        self.assertEqual(test.content.rendered, '<strong>hello world!</strong>')
        self.assertEqual(len(test.content), markup_content_len)
        with self.assertRaises(AttributeError):
            print(TestableModel.content.rendered)

    def test_bad_markup_language_config_should_raise(self):
        # Run & check
        machina_settings.MACHINA_MARKUP_LANGUAGE = (('it.will.fail'), {})
        with self.assertRaises(ImproperlyConfigured):
            reload(fields)
        del machina_settings.MACHINA_MARKUP_LANGUAGE
        with self.assertRaises(ImproperlyConfigured):
            reload(fields)


class ExtendedImageFieldTestCase(TestCase):
    def setUp(self):
        # Set up some images used for doing image tests
        TEST_ROOT = os.path.abspath(os.path.dirname(__file__))
        settings.MEDIA_ROOT = os.path.join(TEST_ROOT, 'testdata/media/')
        images_dict = {}

        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + "/to_be_resized_image.png", "rb")
        images_dict['to_be_resized_image'] = File(f)

        # Fetch a big image
        f = open(settings.MEDIA_ROOT + "/too_large_image.jpg", "rb")
        images_dict['too_large_image'] = File(f)

        # Fetch a wide image
        f = open(settings.MEDIA_ROOT + "/too_wide_image.jpg", "rb")
        images_dict['too_wide_image'] = File(f)

        # Fetch a high image
        f = open(settings.MEDIA_ROOT + "/too_high_image.jpg", "rb")
        images_dict['too_high_image'] = File(f)

        self.images_dict = images_dict

    def tearDown(self):
        for img in self.images_dict.values():
            img.close()
        tests = TestableModel.objects.all()
        for test in tests:
            try:
                test.resized_image.delete()
            except:
                pass
            try:
                test.validated_image.delete()
            except:
                pass

    def test_resized_image_saving(self):
        # Setup
        test = TestableModel()
        # Run
        field = test._meta.get_field('resized_image')
        field.save_form_data(test, self.images_dict['to_be_resized_image'])
        test.full_clean()
        test.save()
        # Check
        image = Image.open(BytesIO(test.resized_image.read()))
        self.assertEqual(image.size, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))

    def test_image_cleaning(self):
        # Setup
        test = TestableModel()
        field = test._meta.get_field('validated_image')
        invalid_images = ['too_large_image', 'too_wide_image', 'too_high_image', ]
        # Run & check
        for img in invalid_images:
            field.save_form_data(test, self.images_dict[img])
            with self.assertRaises(ValidationError):
                test.full_clean()
