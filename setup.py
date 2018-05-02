# !/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command, find_packages

# Package meta-data.
NAME = 'xthematic'
DESCRIPTION = 'cli app for customizing terminals'
KEYWORDS = 'cli application terminal emulator theme customize X XResources'
URL = 'https://github.com/taesko/xthematic'
AUTHOR = 'Antonio Todorov'
EMAIL = 'taeskow@gmail.com'
REQUIRES_PYTHON = '>=3.6.0'
REQUIRED_FOR_INSTALL = ['click', 'xparser', 'sty']
REQUIRED_FOR_TESTS = ['pytest', 'pytest-runner']
VERSION = None

root = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in MANIFEST.in file!
with io.open(os.path.join(root, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(root, 'src', NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(root, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag -a v{0} -m "version {0}"'.format(about['__version__']))
        os.system('git push --tags')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIRED_FOR_INSTALL,
    tests_require=REQUIRED_FOR_TESTS,
    include_package_data=True,
    entry_points='''
        [console_scripts]
        xthematic=xthematic.cli:main
    ''',
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Pytest',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'Topic :: Utilities'
    ],
    # $ setup.py publish support.
    cmdclass={
        'upload': UploadCommand,
    },
)
