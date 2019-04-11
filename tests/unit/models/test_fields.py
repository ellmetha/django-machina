import pytest
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.files import File
from django.utils.encoding import force_text
from django.utils.six import BytesIO
from tests.models import RESIZED_IMAGE_HEIGHT, RESIZED_IMAGE_WIDTH, DummyModel

from machina.conf import settings as machina_settings
from machina.core.compat import PILImage as Image
from machina.models import fields


try:
    from imp import reload
except ImportError:
    pass


@pytest.mark.django_db
class TestMarkupTextField(object):
    MARKUP_TEXT_FIELD_TESTS = (
        ('**hello _world!_**', '<p><strong>hello <em>world!</em></strong></p>'),
        ('**안녕하세요**', '<p><strong>안녕하세요</strong></p>'),
    )

    def test_can_accept_none_values(self):
        # Setup
        test = DummyModel()
        test.content = None
        # Run
        test.save()
        # Check
        assert test.content is None
        rendered = hasattr(test.content, 'rendered')
        assert not rendered

    def test_correctly_saves_its_data(self):
        # Run & check
        for markup_text, expected_html_text in self.MARKUP_TEXT_FIELD_TESTS:
            test = DummyModel()
            test.content = markup_text
            test.save()
            assert test.content.rendered.rstrip() == expected_html_text

    def test_provides_access_to_the_raw_text_and_to_the_rendered_text(self):
        # Setup
        test = DummyModel()
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
        assert field.value_to_string(test) == markup_content
        assert test.content.rendered.rstrip() == '<p><strong>hello world!</strong></p>'
        assert len(test.content) == markup_content_len
        with pytest.raises(AttributeError):
            print(DummyModel.content.rendered)

    def test_content_returns_the_raw_value_when_converted_to_a_string(self):
        # Setup
        test = DummyModel()
        test.content = '**hello world!**'
        test.save()
        # Run & check
        assert force_text(test.content) == '**hello world!**'

    def test_should_not_allow_non_accessible_markup_languages(self):
        # Run & check
        machina_settings.MARKUP_LANGUAGE = (('it.will.fail'), {})
        with pytest.raises(ImproperlyConfigured):
            reload(fields)
        del machina_settings.MARKUP_LANGUAGE
        with pytest.raises(ImproperlyConfigured):
            reload(fields)

    def test_should_use_a_default_text_input_widget_with_formfields(self):
        # Setup
        machina_settings.MARKUP_WIDGET = None
        machina_settings.MARKUP_WIDGET_KWARGS = {}

        class TestableForm(forms.ModelForm):
            class Meta:
                model = DummyModel
                exclude = []

        # Run
        form = TestableForm()

        # Check
        assert type(form.fields['content'].widget) == forms.Textarea

    def test_sets_the_markup_widget_to_a_textarea_if_it_is_none(self):
        # Setup
        machina_settings.MARKUP_WIDGET = None
        # Run
        widget_class = fields._get_markup_widget()
        # Check
        assert widget_class == forms.Textarea

    def test_can_use_a_custom_form_widget(self):
        # Setup
        machina_settings.MARKUP_WIDGET = 'django.forms.HiddenInput'
        machina_settings.MARKUP_WIDGET_KWARGS = {}

        class TestableForm(forms.ModelForm):
            class Meta:
                model = DummyModel
                exclude = []
        # Run
        form = TestableForm()
        # Check
        assert isinstance(form.fields['content'].widget, forms.HiddenInput)
        machina_settings.MARKUP_WIDGET = None

    def test_should_not_allow_non_accessible_custom_form_widgets(self):
        # Setup
        machina_settings.MARKUP_WIDGET = 'it.will.fail'
        # Run & check
        with pytest.raises(ImproperlyConfigured):
            class TestableForm(forms.ModelForm):
                class Meta:
                    model = DummyModel
                    exclude = []
        machina_settings.MARKUP_WIDGET = None


@pytest.mark.django_db
class TestExtendedImageField(object):
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        # Set up some images used for doing image tests
        images_dict = {}

        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + "/to_be_resized_image.png", "rb")
        images_dict['to_be_resized_image'] = File(f)

        # Fetch a big image
        f = open(settings.MEDIA_ROOT + "/too_large_image.jpg", "rb")
        images_dict['too_large_image'] = File(f)

        # Fetch a wide image
        f = open(settings.MEDIA_ROOT + "/too_wide_image.jpg", "rb")
        images_dict['too_wide_image'] = File(f)

        # Fetch a high image
        f = open(settings.MEDIA_ROOT + "/too_high_image.jpg", "rb")
        images_dict['too_high_image'] = File(f)

        self.images_dict = images_dict

        yield

        # teardown
        # --

        for img in self.images_dict.values():
            img.close()
        tests = DummyModel.objects.all()
        for test in tests:
            try:
                test.resized_image.delete()
            except:  # noqa: E722
                pass
            try:
                test.validated_image.delete()
            except:  # noqa: E722
                pass

    def test_can_resize_images_before_saving_them(self):
        # Setup
        test = DummyModel()
        # Run
        field = test._meta.get_field('resized_image')
        field.save_form_data(test, self.images_dict['to_be_resized_image'])
        test.full_clean()
        test.save()
        # Check
        image = Image.open(BytesIO(test.resized_image.read()))
        assert image.size == (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT)

    def test_should_not_accept_images_with_incorrect_sizes_or_dimensions(self):
        # Setup
        test = DummyModel()
        field = test._meta.get_field('validated_image')
        invalid_images = ['too_large_image', 'too_wide_image', 'too_high_image', ]
        # Run & check
        for img in invalid_images:
            field.save_form_data(test, self.images_dict[img])
            with pytest.raises(ValidationError):
                test.full_clean()
