#!/usr/bin/env python

##############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

from setuptools import setup, find_packages

description = "Taurus extension providing pyqtgraph-based widgets"

long_description = """taurus_pyqtgraph is an extension for the Taurus package.
It adds the taurus.qt.qtgui.tpg submodule which provides pyqtgraph-based
widgets."""

author = "Taurus Community"

maintainer = author

maintainer_email = "tauruslib-devel@lists.sourceforge.net"

url = "https://github.com/taurus-org/taurus_pyqtgraph"

download_url = url

platforms = ["Linux", "Windows"]

keywords = ["Taurus", "pyqtgraph", "plugin", "widgets"]

install_requires = ["pyqtgraph", "click", "taurus>=4.5.2", "lxml", "ply"]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

entry_points = {
    "taurus.qt.qtgui": ["tpg = taurus_pyqtgraph"],
    "taurus.cli.subcommands": ["tpg = taurus_pyqtgraph.cli:tpg"],
}

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: X11 Applications :: Qt",
    "Environment :: Win32 (MS Windows)",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    (
        "License :: OSI Approved :: "
        + "GNU Lesser General Public License v3 or later (LGPLv3+)"
    ),
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Unix",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Libraries",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Software Development :: Widget Sets",
]


setup(
    name="taurus_pyqtgraph",
    version="0.3.2",
    description=description,
    long_description=long_description,
    author=author,
    maintainer=maintainer,
    maintainer_email=maintainer_email,
    url=url,
    download_url=download_url,
    platforms=platforms,
    license="LGPLv3+",
    keywords=keywords,
    packages=find_packages(),
    classifiers=classifiers,
    include_package_data=True,
    entry_points=entry_points,
    test_suite="tests",
    tests_require=test_requirements,
    install_requires=install_requires,
    setup_requires=setup_requirements,
)
