#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os

from setuptools import setup, find_packages

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

requires = [
    'certifi==2018.8.24',
    'chardet==3.0.4',
    'configparser==3.5.0',
    'Deprecated==1.2.3',
    'enum34==1.1.6',
    'flake8==3.5.0',
    'idna==2.7',
    'mccabe==0.6.1',
    'pycodestyle==2.3.1',
    'pyflakes==1.6.0',
    'PyGithub==1.43.2',
    'PyJWT==1.6.4',
    'requests==2.19.1',
    'urllib3==1.23',
    'wrapt==1.10.11']

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'pkg_tracker',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev4')

setup(
    name="pkg_tracker",
    version=version,
    url='https://github.com/hosmada/pkg_tracker',
    author='hosmada',
    author_email='usodamasijp@gmail.com',
    maintainer='hosmada',
    maintainer_email='usodamasijp@gmail.com',
    description='open pull request via circle-ci',
    long_description=readme,
    packages=find_packages(),
    install_requires=requires,
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
          'console_scripts': [
          'pkgtrack = pkg_tracker.update:update'
          ]
        },
)
