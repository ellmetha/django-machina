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
    long_description=read_relative_file('README.rst'),
    zip_safe=False,
    install_requires=[
        'django>=1.4.2',
        'django-model-utils==1.5.0',

        # Django-mptt is required to handle the tree hierarchy of nested forums
        'django-mptt>=0.6.1,<0.7',

        # Django-guardian is used to provide a powerful per-forum object permission system
        'django-guardian>=1.2,<1.3',

        # Machina uses Django-haystack to provide search support
        'django-haystack>=2.1.0',

        # Pillow is required for image fields
        'pillow>=1.7.8,<2.3',

        # Machina uses BBCode by default as a syntax for forum messages ; but you can change this
        'django-precise-bbcode>=0.4.1,<0.5',

        # Machina's default templates use django-bootstrap3 to render forms ; but you can override this
        'django-bootstrap3>=3.3.0,<3.4',
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
