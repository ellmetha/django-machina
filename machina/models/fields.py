# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import path

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models import signals
from django.forms import Textarea
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.encoding import python_2_unicode_compatible
from django.utils.encoding import smart_str
from django.utils.functional import curry
from django.utils.safestring import SafeData
from django.utils.safestring import mark_safe
from django.utils.six import BytesIO
from django.utils.translation import ugettext_lazy as _

from machina.conf import settings as machina_settings


_rendered_field_name = lambda name: '_{}_rendered'.format(name)


def _get_markup_widget():
    dotted_path = machina_settings.MACHINA_MARKUP_WIDGET
    try:
        assert dotted_path is not None
        module, widget = dotted_path.rsplit('.', 1)
        module, widget = smart_str(module), smart_str(widget)
        widget = getattr(__import__(module, {}, {}, [widget]), widget)
        return widget
    except ImportError as e:
        raise ImproperlyConfigured(_('Could not import MACHINA_MARKUP_WIDGET {}: {}').format(
            machina_settings.MACHINA_MARKUP_WIDGET,
            e))
    except AssertionError:
        return Textarea


MarkupTextFieldWidget = _get_markup_widget()


def _get_render_function(dotted_path, kwargs):
    module, func = dotted_path.rsplit('.', 1)
    module, func = smart_str(module), smart_str(func)
    func = getattr(__import__(module, {}, {}, [func]), func)
    return curry(func, **kwargs)


try:
    markup_lang = machina_settings.MACHINA_MARKUP_LANGUAGE
    render_func = _get_render_function(markup_lang[0], markup_lang[1]) if markup_lang \
        else lambda text: text
except ImportError as e:
    raise ImproperlyConfigured(_('Could not import MACHINA_MARKUP_LANGUAGE {}: {}').format(
        machina_settings.MACHINA_MARKUP_LANGUAGE,
        e))
except AttributeError as e:
    raise ImproperlyConfigured(_('MACHINA_MARKUP_LANGUAGE setting is required'))


@python_2_unicode_compatible
class MarkupText(SafeData):
    def __init__(self, instance, field_name, rendered_field_name):
        # Stores a reference to the instance along with field names
        # to make assignment possible.
        self.instance = instance
        self.field_name = field_name
        self.rendered_field_name = rendered_field_name

    # raw is read/write
    def _get_raw(self):
        return self.instance.__dict__[self.field_name]

    def _set_raw(self, val):
        setattr(self.instance, self.field_name, val)

    raw = property(_get_raw, _set_raw)

    # rendered is a read only property
    def _get_rendered(self):
        return mark_safe(getattr(self.instance, self.rendered_field_name))

    rendered = property(_get_rendered)

    # Allows display via templates to work without safe filter
    def __str__(self):
        return self.raw

    # Return the length of the rendered string so that bool tests work as expected
    def __len__(self):
        return len(self.raw)


class MarkupTextDescriptor(object):
    """
    Acts as the Django's default attribute descriptor class, enabled via the SubfieldBase metaclass.
    The main difference is that it does not call to_python() on the MarkupTextField class. Instead,
    it stores the two different values of a markup content (the raw and the rendered data)
    separately. These values can be separately updated when something is assigned. When the field is
    accessed, a MarkupText instance will be returned ; this one is built with the current data.
    """
    def __init__(self, field):
        self.field = field
        self.rendered_field_name = _rendered_field_name(self.field.name)

    def __get__(self, instance, owner):
        if instance is None:
            return None
        raw = instance.__dict__[self.field.name]
        if raw is None:
            return None
        return MarkupText(instance, self.field.name, self.rendered_field_name)

    def __set__(self, instance, value):
        if isinstance(value, MarkupText):
            instance.__dict__[self.field.name] = value.raw
            setattr(instance, self.rendered_field_name, value.rendered)
        else:
            # Set only the raw field
            instance.__dict__[self.field.name] = value


class MarkupTextField(models.TextField):
    """
    A MarkupTextField contributes two columns to the model instead of the standard single column.
    The initial column store any content written by using a given markup language and the other one
    keeps the rendered content returned by a specific render function.
    """
    def __init__(self, *args, **kwargs):
        # For Django 1.7 migration serializer compatibility: the frozen version of a
        # MarkupTextField can't try to add a '*_rendered' field, because the '*_rendered' field
        # itself is frozen / serialized as well.
        self.add_rendered_field = not kwargs.pop('no_rendered_field', False)
        super(MarkupTextField, self).__init__(*args, **kwargs)

    def deconstruct(self):  # pragma: no cover
        """
        As outlined in the Django 1.7 documentation, this method tells Django how to take an
        instance of a new field in order to reduce it to a serialized form. This can be used to
        configure what arguments need to be passed to the __init__() method of the field in order to
        re-create it. We use it in order to pass the 'no_rendered_field' to the __init__() method.
        This will allow the _rendered field to not be added to the model class twice.
        """
        name, import_path, args, kwargs = super(MarkupTextField, self).deconstruct()
        kwargs['no_rendered_field'] = True
        return name, import_path, args, kwargs

    def contribute_to_class(self, cls, name):
        if self.add_rendered_field and not cls._meta.abstract:
            rendered_field = models.TextField(editable=False, blank=True, null=True)
            cls.add_to_class(_rendered_field_name(name), rendered_field)

        # The data will be rendered before each save
        signals.pre_save.connect(self.render_data, sender=cls)

        # Add the default text field
        super(MarkupTextField, self).contribute_to_class(cls, name)

        # Associates the name of this field to a special descriptor that will return
        # an appropriate Markup object each time the field is accessed
        setattr(cls, name, MarkupTextDescriptor(self))

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return value.raw

    def get_db_prep_value(self, value, connection=None, prepared=False):
        try:
            return value.raw
        except AttributeError:
            return value

    def render_data(self, signal, sender, instance=None, **kwargs):
        value = getattr(instance, self.attname)

        rendered = None
        if hasattr(value, 'raw'):
            rendered = render_func(value.raw)

        setattr(instance, _rendered_field_name(self.attname), rendered)

    def formfield(self, **kwargs):
        widget = _get_markup_widget()
        defaults = {'widget': widget(**machina_settings.MACHINA_MARKUP_WIDGET_KWARGS)}
        defaults.update(kwargs)
        field = super(MarkupTextField, self).formfield(**defaults)
        return field


class ExtendedImageField(models.ImageField):
    """
    An ExtendedImageField is an ImageField whose image can be resized before being saved.
    This field also add the capability of checking the image size, width and height a user may send.
    """
    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        # Both min_width and max_width must be provided in order to be used
        self.min_width = kwargs.pop('min_width', None)
        self.max_width = kwargs.pop('max_width', None)
        # Both min_height and max_height must be provided in order to be used
        self.min_height = kwargs.pop('min_height', None)
        self.max_height = kwargs.pop('max_height', None)
        self.max_upload_size = kwargs.pop('max_upload_size', 0)
        super(ExtendedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        from django.core.files.images import get_image_dimensions
        data = super(ExtendedImageField, self).clean(*args, **kwargs)
        image = data.file

        # Controls the file size
        if self.max_upload_size and hasattr(image, 'size'):
            if image.size > self.max_upload_size:
                raise ValidationError(
                    _('Files of size greater than {} are not allowed. Your file is {}').format(
                        filesizeformat(self.max_upload_size),
                        filesizeformat(image.size)
                    )
                )

        # Controls the image size
        image_width, image_height = get_image_dimensions(data)
        if self.min_width and self.max_width \
                and not self.min_width <= image_width <= self.max_width:
            raise ValidationError(
                _('Images of width lesser than {}px or greater than {}px or are not allowed. '
                  'The width of your image is {}px').format(
                    self.min_width, self.max_width, image_width))
        if self.min_height and self.max_height \
                and not self.min_height <= image_height <= self.max_height:
            raise ValidationError(
                _('Images of height lesser than {}px or greater than {}px or are not allowed. '
                  'The height of your image is {}px').format(
                    self.min_height, self.max_height, image_height))

        return data

    def save_form_data(self, instance, data):
        if data and self.width and self.height:
            content = self.resize_image(data.read(), (self.width, self.height))

            # Handle the filename because the image will be converted to PNG
            filename = path.splitext(path.split(data.name)[-1])[0]
            filename = '{}.png'.format(filename)

            # Regenerate a File object
            data = SimpleUploadedFile(filename, content)
        super(ExtendedImageField, self).save_form_data(instance, data)

    def resize_image(self, data, size):
        """
        Resizes the given image to fit inside a box of the given size
        """
        from machina.core.compat import PILImage as Image
        image = Image.open(BytesIO(data))

        # Resize!
        image.thumbnail(size, Image.ANTIALIAS)

        string = BytesIO()
        image.save(string, format='PNG')
        return string.getvalue()
