#!/usr/bin/env python

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

from __future__ import absolute_import

__all__ = ["TaurusPlot"]

from future.utils import string_types
import copy
from taurus.external.qt import QtGui, Qt
from taurus.core.util.containers import LoopList
from taurus.core.util.log import Logger
from taurus.qt.qtcore.configuration import BaseConfigurableClass

from pyqtgraph import PlotWidget

from .curvespropertiestool import CurvesPropertiesTool
from .taurusmodelchoosertool import TaurusXYModelChooserTool
from .legendtool import PlotLegendTool
from .datainspectortool import DataInspectorTool
from .y2axis import Y2ViewBox
from .curveproperties import CURVE_COLORS


class TaurusPlot(PlotWidget, BaseConfigurableClass):
    """
    TaurusPlot is a general widget for plotting 1D data sets. It is an extended
    taurus-aware version of :class:`pyqtgraph.PlotWidget`.

    Apart from all the features already available in a regulat PlotWidget,
    TaurusPlot incorporates the following tools/features:

        - Secondary Y axis (right axis)
        - A plot configuration dialog, and save/restore configuration
          facilities
        - A menu option for adding/removing models
        - A menu option for showing/hiding the legend
        - Automatic color change of curves for newly added models

    """

    def __init__(self, parent=None, **kwargs):
        if Qt.QT_VERSION < 0x050000:
            # Workaround for issue when using super with pyqt<5
            BaseConfigurableClass.__init__(self)
            PlotWidget.__init__(self, parent=parent, **kwargs)
        else:
            super(TaurusPlot, self).__init__(parent=None, **kwargs)

        # Compose with a Logger
        self._logger = Logger(name=self.__class__.__name__)
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.warning = self._logger.warning
        self.error = self._logger.error

        # set up cyclic color generator
        self._curveColors = LoopList(CURVE_COLORS)
        self._curveColors.setCurrentIndex(-1)

        # add save & retrieve configuration actions
        menu = self.getPlotItem().getViewBox().menu
        saveConfigAction = QtGui.QAction("Save configuration", menu)
        saveConfigAction.triggered.connect(self._onSaveConfigAction)
        menu.addAction(saveConfigAction)

        loadConfigAction = QtGui.QAction("Retrieve saved configuration", menu)
        loadConfigAction.triggered.connect(self._onRetrieveConfigAction)
        menu.addAction(loadConfigAction)

        self.registerConfigProperty(self._getState, self.restoreState, "state")

        # add legend tool
        legend_tool = PlotLegendTool(self)
        legend_tool.attachToPlotItem(self.getPlotItem())

        # add model chooser
        self._model_chooser_tool = TaurusXYModelChooserTool(self)
        self._model_chooser_tool.attachToPlotItem(
            self.getPlotItem(), self, self._curveColors
        )

        # add Y2 axis
        self._y2 = Y2ViewBox()
        self._y2.attachToPlotItem(self.getPlotItem())

        # add plot configuration dialog
        self._cprop_tool = CurvesPropertiesTool(self)
        self._cprop_tool.attachToPlotItem(self.getPlotItem(), y2=self._y2)

        # add a data inspector
        inspector_tool = DataInspectorTool(self)
        inspector_tool.attachToPlotItem(self.getPlotItem())

        # enable Autorange
        self.getPlotItem().getViewBox().enableAutoRange(True)
        self._y2.enableAutoRange(True)

        # Register config properties
        self.registerConfigDelegate(self._model_chooser_tool, "XYmodelchooser")
        self.registerConfigDelegate(self._y2, "Y2Axis")
        self.registerConfigDelegate(self._cprop_tool, "CurvePropertiesTool")
        self.registerConfigDelegate(legend_tool, "legend")
        self.registerConfigDelegate(inspector_tool, "inspector")

    # --------------------------------------------------------------------
    # workaround for bug in pyqtgraph v<=0.10.0, already fixed in
    # https://github.com/pyqtgraph/pyqtgraph/commit/52754d4859
    # TODO: remove this once pyqtgraph v>0.10 is released
    def __getattr__(self, item):
        try:
            return PlotWidget.__getattr__(self, item)
        except NameError:
            raise AttributeError(
                "{} has no attribute {}".format(self.__class__.__name__, item)
            )

    # --------------------------------------------------------------------

    def __getitem__(self, idx):
        """
        Provides a list-like interface: items can be accessed using slice
        notation
        """
        return self.getPlotItem().listDataItems()[idx]

    def __len__(self):
        return len(self.getPlotItem().listDataItems())

    def setModel(self, names):
        """Reimplemented to delegate to the model chooser"""
        # support passing a string in names
        if isinstance(names, string_types):
            names = [names]
        self._model_chooser_tool.updateModels(names)

    def addModels(self, names):
        """Reimplemented to delegate to the  model chooser"""
        # support passing a string in names
        if isinstance(names, string_types):
            names = [names]
        self._model_chooser_tool.addModels(names)

    def _getState(self):
        """Same as PlotWidget.saveState but removing viewRange conf to force
        a refresh with targetRange when loading
        """
        state = copy.deepcopy(self.saveState())
        # remove viewRange conf
        del state["view"]["viewRange"]
        return state

    def setXAxisMode(self, x_axis_mode):
        """Required generic TaurusPlot API """
        from taurus_pyqtgraph import DateAxisItem

        if x_axis_mode == "t":
            axis = DateAxisItem(orientation="bottom")
            axis.attachToPlotItem(self.getPlotItem())
        elif x_axis_mode == "n":
            axis = self.getPlotItem().axes["bottom"]["item"]
            if isinstance(axis, DateAxisItem):
                axis.detachFromPlotItem()
        else:
            raise ValueError("Unsupported x axis mode {}".format(x_axis_mode))

    def _onSaveConfigAction(self):
        """wrapper to avoid issues with overloaded signals"""
        return self.saveConfigFile()

    def _onRetrieveConfigAction(self):
        """wrapper to avoid issues with overloaded signals"""
        return self.loadConfigFile()


def plot_main(
    models=(),
    config_file=None,
    x_axis_mode="n",
    demo=False,
    window_name="TaurusPlot (pg)",
):
    """Launch a TaurusPlot"""
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None, app_name="taurusplot(pg)")

    w = TaurusPlot()

    # w.loadConfigFile('tmp/TaurusPlot.pck')

    w.setWindowTitle(window_name)

    if demo:
        models = list(models)
        models.extend(["eval:rand(100)", "eval:0.5*sqrt(arange(100))"])

    w.setXAxisMode(x_axis_mode.lower())

    if config_file is not None:
        w.loadConfigFile(config_file)

    if models:
        w.setModel(models)

    w.show()
    ret = app.exec_()

    # import pprint
    # pprint.pprint(w.createConfig())

    sys.exit(ret)


if __name__ == "__main__":
    plot_main()
