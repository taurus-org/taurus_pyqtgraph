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

import pkg_resources
import click

_tpg_version = pkg_resources.require("taurus_pyqtgraph")[0].version
_taurus_version = pkg_resources.require("taurus")[0].version
_version = "{0} (with taurus {1})".format(_tpg_version, _taurus_version)


@click.group("tpg")
@click.version_option(version=_version, prog_name="tpg")
def tpg():
    """Taurus-pyqtgraph related commands"""
    pass


@tpg.command("plot")
@click.argument("models", nargs=-1)
@click.option(
    "--config",
    "config_file",
    type=click.File(),
    help="configuration file for initialization",
)
@click.option(
    "-x",
    "--x-axis-mode",
    "x_axis_mode",
    type=click.Choice(["t", "n"]),
    default="n",
    show_default=True,
    help=(
        'X axis mode. "t" implies using a Date axis'
        + '"n" uses the regular axis'
    ),
)
@click.option("--demo", is_flag=True, help="show a demo of the widget")
@click.option(
    "--window-name",
    "window_name",
    default="TaurusPlot (pg)",
    help="Name of the window",
)
def plot_cmd(models, config_file, x_axis_mode, demo, window_name):
    """Shows a plot for the given models"""
    from .plot import plot_main

    return plot_main(
        models=models,
        config_file=config_file,
        x_axis_mode=x_axis_mode,
        demo=demo,
        window_name=window_name,
    )


@tpg.command("trend")
@click.argument("models", nargs=-1)
@click.option(
    "--config",
    "config_file",
    type=click.File(),
    help="configuration file for initialization",
)
@click.option("--demo", is_flag=True, help="show a demo of the widget")
@click.option(
    "--window-name",
    "window_name",
    default="TaurusPlot (pg)",
    help="Name of the window",
)
def trend_cmd(models, config_file, demo, window_name):
    """Shows a trend for the given models"""
    from .trend import trend_main

    return trend_main(
        models=models,
        config_file=config_file,
        demo=demo,
        window_name=window_name,
    )


if __name__ == "__main__":
    import sys

    sys.exit(tpg())  # pragma: no cover
