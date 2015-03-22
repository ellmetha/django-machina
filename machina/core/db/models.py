# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django import VERSION as DJANGO_VERSION
from django.utils.importlib import import_module

# Local application / specific library imports


# The following is mainly inspired from the model loading tools provided
# by django-oscar to handle overridable model classes.

if DJANGO_VERSION < (1, 7):  # pragma: no cover

    from django.db.models import get_model as django_get_model

    def get_model(app_label, model_name, *args, **kwargs):
        """
        Given an app label and a model name, returns the corresponding model class.
        """
        model = django_get_model(app_label, model_name, *args, **kwargs)
        return model

    def is_model_registered(app_label, model_name):
        """
        Checks whether the given model is registered or not. It is usefull to prevent
        Machina models for being registered if they are overridden by local apps.
        """
        return bool(django_get_model(app_label, model_name, seed_cache=False))

else:

    from django.apps import apps
    from django.apps.config import MODELS_MODULE_NAME
    from django.core.exceptions import AppRegistryNotReady

    def get_model(app_label, model_name):
        """
        Fetches a Django model using the app registry.

        This doesn't require that an app with the given app label exists,
        which makes it safe to call when the registry is being populated.
        All other methods to access models might raise an exception about the
        registry not being ready yet.
        Raises LookupError if model isn't found.
        """
        try:
            return apps.get_model(app_label, model_name)
        except AppRegistryNotReady:
            if apps.apps_ready and not apps.models_ready:
                # If this function is called while `apps.populate()` is
                # loading models, ensure that the module that defines the
                # target model has been imported and try looking the model up
                # in the app registry. This effectively emulates
                # `from path.to.app.models import Model` where we use
                # `Model = get_model('app', 'Model')` instead.
                app_config = apps.get_app_config(app_label)
                # `app_config.import_models()` cannot be used here because it
                # would interfere with `apps.populate()`.
                import_module('%s.%s' % (app_config.name, MODELS_MODULE_NAME))
                # In order to account for case-insensitivity of model_name,
                # look up the model through a private API of the app registry.
                return apps.get_registered_model(app_label, model_name)
            else:
                # This must be a different case (e.g. the model really doesn't
                # exist). We just re-raise the exception.
                raise

    def is_model_registered(app_label, model_name):
        """
        Checks whether the given model is registered or not. It is usefull to prevent
        Machina models for being registered if they are overridden by local apps.
        """
        try:
            apps.get_registered_model(app_label, model_name)
        except LookupError:
            return False
        else:
            return True


def model_factory(abstract_class):
    """
    Given an abstract class, constructs the model that inherits  from this class only
    if a model with the same (app label, model name) was not already in the app registry.
    """
    app_label = abstract_class.Meta.app_label
    model_name = abstract_class.__name__.replace('Abstract', '')

    if not is_model_registered(app_label, model_name):
        return type(model_name, (abstract_class, ), {'__module__': __name__, })
