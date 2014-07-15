# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from django.conf import settings
from django.utils.importlib import import_module

# Local application / specific library imports


class AppNotFoundError(Exception):
    pass


class ClassNotFoundError(Exception):
    pass


def get_class(module_label, classname):
    return get_classes(module_label, [classname, ])[0]


def get_classes(module_label, classnames):
    """
    Imports a set of classes from a given module.

    Usage::

        get_classes('forum.models', ['Forum', 'ForumReadTrack', ])

    """
    app_label = module_label.split('.')[0]

    app_module_path = _get_app_module_path(module_label)
    if not app_module_path:
        raise AppNotFoundError('No app found matching \'{}\''.format(module_label))

    # Determines the full module path by appending the module label
    # to the base package path of the considered application.
    module_path = app_module_path
    if '.' in app_module_path:
        base_package = app_module_path.rsplit('.' + app_label, 1)[0]
        module_path = '{}.{}'.format(base_package, module_label)

    # Try to import this module from the related app that is specified
    # in the Django settings.
    local_imported_module = _import_module(module_path)

    # If the previous import failed and if the module we tried to import
    # was not located inside the machina vanilla apps, try to import it
    # from the corresponding machina app.
    machina_imported_module = None
    if local_imported_module is None and not app_module_path.startwith('machina.apps'):
        machina_imported_module = _import_module('{}.{}'.format('machina.apps', module_label))

    if local_imported_module is None and machina_imported_module is None:
        raise AppNotFoundError('Error importing \'{}\''.format(module_path))

    imported_module = local_imported_module or machina_imported_module
    return _pick_up_classes(imported_module, classnames)


def _import_module(module_path):
    """
    Import the given Python module path.
    """
    try:
        imported_module = import_module(module_path)
        return imported_module
    except ImportError:
        return None


def _pick_up_classes(module, classnames):
    """
    Given a list of class names to retrieve, try to fetch them from the specified
    module.
    Returns the list of fetched classes.
    """
    klasses = []
    for classname in classnames:
        klass = None
        if hasattr(module, classname):
            klass = getattr(module, classname)
        if not klass:
            raise ClassNotFoundError('Error fetching \'{}\' in {}'.format(classname, module.__name__))
        klasses.append(klass)
    return klasses


def _get_app_module_path(module_label):
    """
    Given a module label, loop over the apps specified in the INSTALLED_APPS
    to find the corresponding application module path.
    """
    app_name = module_label.rsplit('.', 1)[0]
    for app in settings.INSTALLED_APPS:
        if app.endswith('.' + app_name) or app == app_name:
            return app
    return None
