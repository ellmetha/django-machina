# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import traceback

from django.conf import settings


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
    # to the base package path of the considered application.
    module_path = app_module_path
    if '.' in app_module_path:
        base_package = app_module_path.rsplit('.' + app_label, 1)[0]
        module_path = '{}.{}'.format(base_package, module_label)

    # Try to import this module from the related app that is specified
    # in the Django settings.
    local_imported_module = _import_module(module_path, classnames)

    # If the module we tried to import is not located inside the machina
    # vanilla apps, try to import it from the corresponding machina app.
    machina_imported_module = None
    if not app_module_path.startswith('machina.apps'):
        machina_imported_module = _import_module(
            '{}.{}'.format('machina.apps', module_label), classnames)

    if local_imported_module is None and machina_imported_module is None:
        raise AppNotFoundError('Error importing \'{}\''.format(module_path))

    # Any local module is prioritized over the corresponding machina module
    imported_modules = [m for m in (local_imported_module, machina_imported_module) if
                        m is not None]
    return _pick_up_classes(imported_modules, classnames)


def _import_module(module_path, classnames):
    """
    Tries to import the given Python module path.
    """
    try:
        imported_module = __import__(module_path, fromlist=classnames)
        return imported_module
    except ImportError:
        # In case of an ImportError, the module being loaded generally does not
        # exist. But an ImportError can occur if the module being loaded exists
        # and another import located inside it failed.
        #
        # In order to provide a meaningfull traceback, the execution information
        # can be inspected in order to determine which case to consider. If the
        # execution information provides more than a certain amount of frames,
        # this means that an ImportError occured while loading the initial
        # Python module.
        __, __, exc_traceback = sys.exc_info()
        frames = traceback.extract_tb(exc_traceback)
        if len(frames) > 1:
            raise


def _pick_up_classes(modules, classnames):
    """
    Given a list of class names to retrieve, try to fetch them from the specified
    list of modules.
    Returns the list of the fetched classes.
    """
    klasses = []
    for classname in classnames:
        klass = None
        for module in modules:
            if hasattr(module, classname):
                klass = getattr(module, classname)
                break
        if not klass:
            raise ClassNotFoundError('Error fetching \'{}\' in {}'.format(
                classname, str([module.__name__ for module in modules])))
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
