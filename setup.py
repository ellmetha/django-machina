from os.path import abspath
from os.path import dirname
from os.path import join
from setuptools import find_packages
from setuptools import setup


def read_relative_file(filename):
    """
    Returns contents of the given file, whose path is supposed relative
    to this module.
    """
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


setup(
    name='django-machina',
    version=read_relative_file('VERSION').strip(),
    author='Morgan Aubert',
    author_email='morgan.aubert@zoho.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/ellmetha/django-machina',
    license='BSD license, see LICENSE file',
    description='A Django forum engine for building powerful and pretty community driven websites.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    install_requires=[
        "django>=1.4",
        "django-model-utils==1.5.0",
        "south>=0.8.4",

        # Django-mptt is required to handle the tree hierarchy of nested forums
        "django-mptt==0.6.0",

        # Django-guardian is used to provide a powerful per-forum object permission system
        "django-guardian==1.1.1",

        # Pillow is required for image fields
        'pillow>=1.7.8,<2.3',

        # Machina uses BBCode by default as a syntax for forum messages (can be configured)
        'django-precise-bbcode==0.4.1',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
