#############################################################################
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
#############################################################################

import click
import sys


@click.group("tpg")
def tpg():
    """[DEPRECATED] use "taurus plot" or "taurus trend" instead"""
    print(
        '"taurus tpg" subcommand is deprecated. '
        + 'Use "taurus plot" or "taurus trend" instead\n'
    )
    sys.exit(1)


@tpg.command()
def plot():
    """[DEPRECATED] use "taurus plot" instead"""
    sys.exit(1)


@tpg.command()
def trend():
    """[DEPRECATED] use "taurus trend" instead"""
    sys.exit(1)


if __name__ == "__main__":
    sys.exit(tpg())  # pragma: no cover
