#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup
from pytest_sqlalchemy_session import __version__


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


def get_requirements(extra=None):
    extra = extra or "base"
    requirements_path = f"requirements/{extra}.txt"
    with open(requirements_path, "r") as fp:
        return [x.strip() for x in fp.readlines()]


setup(
    name='pytest-sqlalchemy-session',
    version=__version__,
    author='Stanislav Shkitin',
    author_email='stanislav.shkitin@yandex.ru',
    maintainer='Stanislav Shkitin',
    maintainer_email='stanislav.shkitin@yandex.ru',
    license='MIT',
    url='https://github.com/tripcher/pytest-sqlalchemy-session',
    description='A pytest plugin for preserving test isolation that use SQLAlchemy.',
    long_description=read('README.md'),
    py_modules=['pytest_sqlalchemy_session'],
    python_requires='>=3.6',
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest10': [
            'pytest-sqlalchemy-session = pytest_sqlalchemy_session.plugin',
        ],
    },
)
