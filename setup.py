#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Taurus Community",
    author_email='tauruslib-devel@lists.sourceforge.net',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Taurus extension providing pyqtgraph-based widgets",
    entry_points={
        'console_scripts': [
            'taurus_pyqtgraph=taurus_pyqtgraph.cli:main',
        ],
    },
    install_requires=requirements,
    license="LGPLv3+",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='taurus_pyqtgraph',
    name='taurus_pyqtgraph',
    packages=find_packages(include=['taurus_pyqtgraph']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/taurus-org/taurus_pyqtgraph',
    version='0.3.0-alpha',
    zip_safe=False,
)
