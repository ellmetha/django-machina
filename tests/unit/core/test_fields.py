# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import unicode_literals
try:
    from imp import reload
except ImportError:
    pass

# Third party imports
from django import forms
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
from tests.models import RESIZED_IMAGE_HEIGHT
from tests.models import RESIZED_IMAGE_WIDTH
from tests.models import TestableModel


class TestMarkupTextField(TestCase):
    # The following tests involve the django-markdown
    # app. This one can be used with Machina in order to
    # provide a support for the Markdown syntax. But instead
    # we can use another Django app providing support for
    # other syntax (eg. BBCode).
    MARKUP_TEXT_FIELD_TESTS = (
        ('**hello _world!_**', '<p><strong>hello <em>world!</em></strong></p>'),
        ('[goto google](http://google.com)', '<p><a href="http://google.com">goto google</a></p>'),
        ('**안녕하세요**', '<p><strong>안녕하세요</strong></p>'),
    )

    def test_can_accept_none_values(self):
        # Setup
        test = TestableModel()
        test.content = None
        # Run
        test.save()
        # Check
        self.assertIsNone(test.content)
        rendered = hasattr(test.content, 'rendered')
        self.assertFalse(rendered)

    def test_correctly_saves_its_data(self):
        # Run & check
        for markup_text, expected_html_text in self.MARKUP_TEXT_FIELD_TESTS:
            test = TestableModel()
            test.content = markup_text
            test.save()
            self.assertEqual(test.content.rendered, expected_html_text)

    def test_provides_access_to_the_raw_text_and_to_the_rendered_text(self):
        # Setup
        test = TestableModel()
        test.content = '**hello**'
        test.save()
        field = test._meta.get_field('content')
        markup_content = '**hello world!**'
        markup_content_len = len(markup_content)
        # Run
        test.content.raw = markup_content
        markup_bk = test.content
        test.content = markup_bk
        test.save()
        # Check
        self.assertEqual(field.value_to_string(test), markup_content)
        self.assertEqual(test.content.rendered, '<p><strong>hello world!</strong></p>')
        self.assertEqual(len(test.content), markup_content_len)
        with self.assertRaises(AttributeError):
            print(TestableModel.content.rendered)

    def test_should_not_allow_non_accessible_markup_languages(self):
        # Run & check
        machina_settings.MACHINA_MARKUP_LANGUAGE = (('it.will.fail'), {})
        with self.assertRaises(ImproperlyConfigured):
            reload(fields)
        del machina_settings.MACHINA_MARKUP_LANGUAGE
        with self.assertRaises(ImproperlyConfigured):
            reload(fields)

    def test_should_use_a_default_text_input_widget_with_formfields(self):
        # Setup
        class TestableForm(forms.ModelForm):
            class Meta:
                model = TestableModel
        # Run
        form = TestableForm()
        # Check
        self.assertTrue(isinstance(form.fields['content'].widget, forms.Textarea))

    def test_can_use_a_custom_form_widget(self):
        # Setup
        machina_settings.MACHINA_MARKUP_WIDGET = 'django.forms.HiddenInput'

        class TestableForm(forms.ModelForm):
            class Meta:
                model = TestableModel
        # Run
        form = TestableForm()
        # Check
        self.assertTrue(isinstance(form.fields['content'].widget, forms.HiddenInput))
        machina_settings.MACHINA_MARKUP_WIDGET = None

    def test_should_not_allow_non_accessible_custom_form_widgets(self):
        # Setup
        machina_settings.MACHINA_MARKUP_WIDGET = 'it.will.fail'
        # Run & check
        with self.assertRaises(ImproperlyConfigured):
            class TestableForm(forms.ModelForm):
                class Meta:
                    model = TestableModel
        machina_settings.MACHINA_MARKUP_WIDGET = None


class TestExtendedImageField(TestCase):
    def setUp(self):
        # Set up some images used for doing image tests
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

    def test_can_resize_images_before_saving_them(self):
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

    def test_should_not_accept_images_with_incorrect_sizes_or_dimensions(self):
        # Setup
        test = TestableModel()
        field = test._meta.get_field('validated_image')
        invalid_images = ['too_large_image', 'too_wide_image', 'too_high_image', ]
        # Run & check
        for img in invalid_images:
            field.save_form_data(test, self.images_dict[img])
            with self.assertRaises(ValidationError):
                test.full_clean()
