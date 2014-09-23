#!/usr/bin/env python

# Standard library imports
import os
from os.path import dirname
from os.path import realpath
import sys

# Third party imports
import django

# Local application / specific library imports
from tests.settings import configure


def run(verbosity, *args):
    from django_nose import NoseTestSuiteRunner
    runner = NoseTestSuiteRunner(verbosity=verbosity)

    if not args:
        args = ['tests']
    num_failures = runner.run_tests(args)
    if num_failures:
        sys.exit(num_failures)


if __name__ == '__main__':
    args = sys.argv[1:]

    verbosity = 1
    if args:
        # If some args were specified, try to see if any nose options have
        # been specified. If they have, then don't set any.
        has_options = any(map(lambda x: x.startswith('--'), args))
        if has_options:
            # Remove options as nose will pick these up from sys.argv
            for arg in args:
                if arg.startswith('--verbosity'):
                    verbosity = int(arg[-1])
            args = [arg for arg in args if not arg.startswith('-')]

    # Give feedback on used versions
    sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
    sys.stderr.write('Using Django version {0} from {1}\n'.format(
        django.get_version(),
        os.path.dirname(os.path.abspath(django.__file__)))
    )

    # Detect location and available modules
    module_root = dirname(realpath(__file__))

    # Configure Django and machina
    configure()
    if hasattr(django, 'setup'):
        # As outlined in the Django 1.7 release notes, it is now required
        # to explicitly initialize Django at the beginning if any standalone
        # script in order to properly support the Django "app registry".
        django.setup()

    # To infinity... and beyond!
    run(verbosity, *args)
