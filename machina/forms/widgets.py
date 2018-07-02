# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms.widgets import Select
from django.forms.widgets import Textarea


# Originaly comes from https://djangosnippets.org/snippets/2453/
class SelectWithDisabled(Select):
    """ Subclass of Django's select widget that allows disabling options.

    To disable an option, pass a dict instead of a string for its label, of the form:

        {'label': 'option label', 'disabled': True}

    """

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        disabled = False
        if isinstance(label, dict):
            label, disabled = label['label'], label['disabled']
        option_dict = super(SelectWithDisabled, self).create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if disabled:
            option_dict['attrs']['disabled'] = 'disabled'
        return option_dict


class MarkdownTextareaWidget(Textarea):
    """ A simple Textarea widget using the simplemde JS library to provide Markdown editor. """

    class Media:
        css = {
            'all': ('machina/build/css/vendor/simplemde.min.css', ),
        }
        js = (
            'machina/build/js/vendor/simplemde.min.js',
            'machina/build/js/machina.editor.min.js',
        )

    def render(self, name, value, attrs=None, **kwargs):
        attrs = {} if attrs is None else attrs
        classes = attrs.get('classes', '')
        attrs['class'] = classes + ' machina-mde-markdown'
        return super(MarkdownTextareaWidget, self).render(name, value, attrs, **kwargs)
