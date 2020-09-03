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

__all__ = ["TaurusTrend"]

from future.utils import string_types
import copy

from taurus.external.qt import QtGui, Qt
from taurus.core.util.containers import LoopList
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.core.util.log import Logger

from pyqtgraph import PlotWidget

from .curvespropertiestool import CurvesPropertiesTool
from .dateaxisitem import DateAxisItem
from .legendtool import PlotLegendTool
from .forcedreadtool import ForcedReadTool
from .datainspectortool import DataInspectorTool
from .taurusmodelchoosertool import TaurusXYModelChooserTool
from .taurustrendset import TaurusTrendSet
from .y2axis import Y2ViewBox
from .autopantool import XAutoPanTool
from .curveproperties import CURVE_COLORS


class TaurusTrend(PlotWidget, BaseConfigurableClass):
    """
    TaurusTrend is a general widget for plotting the evolution of a value
    over time. It is an extended taurus-aware version of
    :class:`pyqtgraph.PlotWidget`.

    Apart from all the features already available in a regulat PlotWidget,
    TaurusTrend incorporates the following tools/features:

        - Secondary Y axis (right axis)
        - Time X axis
        - A plot configuration dialog, and save/restore configuration
          facilities
        - A menu option for adding/removing taurus  models
        - A menu option for showing/hiding the legend
        - Automatic color change of curves for newly added models

    """

    def __init__(self, parent=None, **kwargs):

        if Qt.QT_VERSION < 0x050000:
            # Workaround for issue when using super with pyqt<5
            BaseConfigurableClass.__init__(self)
            PlotWidget.__init__(self, parent=parent, **kwargs)
        else:
            super(TaurusTrend, self).__init__(parent=parent, **kwargs)

        # Compose with a Logger
        self._logger = Logger(name=self.__class__.__name__)
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.warning = self._logger.warning
        self.error = self._logger.error

        # set up cyclic color generator
        self._curveColors = LoopList(CURVE_COLORS)
        self._curveColors.setCurrentIndex(-1)

        plot_item = self.getPlotItem()
        menu = plot_item.getViewBox().menu

        # add save & retrieve configuration actions
        saveConfigAction = QtGui.QAction("Save configuration", menu)
        saveConfigAction.triggered.connect(self.saveConfigFile)
        menu.addAction(saveConfigAction)

        loadConfigAction = QtGui.QAction("Retrieve saved configuration", menu)
        loadConfigAction.triggered.connect(self.loadConfigFile)
        menu.addAction(loadConfigAction)

        self.registerConfigProperty(self._getState, self.restoreState, "state")

        # add legend tool
        legend_tool = PlotLegendTool(self)
        legend_tool.attachToPlotItem(plot_item)

        # add model chooser
        self._model_chooser_tool = TaurusXYModelChooserTool(
            self, itemClass=TaurusTrendSet, showX=False
        )
        self._model_chooser_tool.attachToPlotItem(
            self.getPlotItem(), self, self._curveColors
        )

        # add Y2 axis
        self._y2 = Y2ViewBox()
        self._y2.attachToPlotItem(plot_item)

        # Add time X axis
        axis = DateAxisItem(orientation="bottom")
        axis.attachToPlotItem(plot_item)

        # add plot configuration dialog
        self._cprop_tool = CurvesPropertiesTool(self)
        self._cprop_tool.attachToPlotItem(plot_item, y2=self._y2)

        # add data inspector widget
        inspector_tool = DataInspectorTool(self)
        inspector_tool.attachToPlotItem(self.getPlotItem())

        # add force read tool
        self._fr_tool = ForcedReadTool(self)
        self._fr_tool.attachToPlotItem(self.getPlotItem())

        # Add the auto-pan ("oscilloscope mode") tool
        self._autopan = XAutoPanTool()
        self._autopan.attachToPlotItem(self.getPlotItem())

        # Register config properties
        self.registerConfigDelegate(self._model_chooser_tool, "XYmodelchooser")
        # self.registerConfigDelegate(self._y2, "Y2Axis")
        self.registerConfigDelegate(self._cprop_tool, "CurvePropertiesTool")
        self.registerConfigDelegate(legend_tool, "legend")
        self.registerConfigDelegate(self._fr_tool, "forceread")
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
        return self._getCurves()[idx]

    def __len__(self):
        return len(self._getCurves())

    def _getCurves(self):
        """returns a flat list with all items from all trend sets"""
        ret = []
        for ts in self.getTrendSets():
            ret += ts[:]
        return ret

    def getTrendSets(self):
        return [
            e
            for e in self.getPlotItem().listDataItems()
            if isinstance(e, TaurusTrendSet)
        ]

    def setModel(self, names):
        """Set a list of models"""
        # support passing a string  in names instead of a sequence
        if isinstance(names, string_types):
            names = [names]
        self._model_chooser_tool.updateModels(names or [])

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
        """Required generic TaurusTrend API """
        if x_axis_mode != "t":
            raise NotImplementedError(  # TODO
                'X mode "{}" not yet supported'.format(x_axis_mode)
            )

    def setForcedReadingPeriod(self, period):
        """Required generic TaurusTrend API """
        self._fr_tool.setPeriod(period)

    def setMaxDataBufferSize(self, buffer_size):
        """Required generic TaurusTrend API """
        raise NotImplementedError(  # TODO
            "Setting the max buffer size is not yet supported by tpg trend"
        )


def trend_main(
    models=(), config_file=None, demo=False, window_name="TaurusTrend (pg)"
):
    """Launch a TaurusTrend"""
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None, app_name="taurustrend(pg)")

    w = TaurusTrend()

    w.setWindowTitle(window_name)

    if demo:
        models = list(models)
        models.extend(["eval:rand()", "eval:1+rand(2)"])

    if config_file is not None:
        w.loadConfigFile(config_file)

    if models:
        w.setModel(models)

    w.show()
    ret = app.exec_()
    # w.saveConfigFile('tmp/TaurusTrend.pck')
    # import pprint
    # pprint.pprint(w.createConfig())

    sys.exit(ret)


if __name__ == "__main__":
    trend_main(models=("eval:rand()", "sys/tg_test/1/ampli"))
