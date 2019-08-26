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

from datetime import datetime

import numpy
from taurus.external.qt import Qt
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus_pyqtgraph import DateAxisItem
from pyqtgraph import SignalProxy, InfiniteLine, TextItem, ScatterPlotItem


class DataInspectorLine(InfiniteLine):
    """
    DataInspectorLine provides a moveable vertical line item that shows labels
    containing the coordinates of the points of existing curves it touches.
    It provides a method to attach it to a PlotItem.

    .. todo:: for now it only works on the main viewbox.
    """

    # TODO: support more than 1 viewbox (e.g. y2axis).
    # TODO: modify anchor of labels so that they are plotted on the left if
    #       they do not fit in the view

    def __init__(
        self,
        date_format="%Y-%m-%d %H:%M:%S",
        y_format="%0.4f",
        trigger_point_size=10,
    ):
        super(DataInspectorLine, self).__init__(angle=90, movable=True)
        self._labels = []
        self._plot_item = None

        self.y_format = y_format
        self.trigger_point_size = trigger_point_size
        self.date_format = date_format
        self._label_style = "background-color: #35393C;"
        self.sigPositionChanged.connect(self._inspect)
        self._highlights = ScatterPlotItem(
            pos=(),
            symbol="s",
            brush="35393C88",
            pxMode=True,
            size=trigger_point_size,
        )
        # hack to make the CurvesPropertiesTool ignore the highlight points
        self._highlights._UImodifiable = False

    def _inspect(self):
        """
        Slot to re inspector line movemethe mouse move event, and perform
        the action on the plot.

        :param evt: mouse event
        """
        xpos = self.pos().x()
        x_px_size, _ = self.getViewBox().viewPixelSize()

        self._removeLabels()
        points = []
        # iterate over the existing curves
        for c in self._plot_item.curves:
            if c is self._highlights:
                continue
            if c.xData is not None:
                # find the index of the closest point of this curve
                adiff = numpy.abs(c.xData - xpos)
                idx = numpy.argmin(adiff)
                # only add a label if the line touches the symbol
                tolerance = 0.5 * max(1, c.opts["symbolSize"]) * x_px_size
                if adiff[idx] < tolerance:
                    points.append((c.xData[idx], c.yData[idx]))

        self._createLabels(points)

    def _createLabels(self, points):
        for x, y in points:
            # create label at x,y
            _x = self._getXValue(x)
            _y = self._getYValue(y)
            text_item = TextItem()
            text_item.setPos(x, y)
            text_item.setHtml(
                (
                    "<div style='{}'> "
                    + "<span><b>x=</b>{} "
                    + "<span><b>y=</b>{}</span> "
                    + "</div>"
                ).format(self._label_style, _x, _y)
            )
            self._labels.append(text_item)
            self._plot_item.addItem(text_item, ignoreBounds=True)
        # Add "highlight" marker at each point
        self._highlights.setData(pos=points)

    def _getXValue(self, x):
        """
        Helper method converting x value to time if necessary

        :param x: current x value
        :return: time or normal x value (depends of the x axis type)
        """
        x_axis = self._plot_item.getAxis("bottom")
        if isinstance(x_axis, DateAxisItem):
            return self._timestampToDateTime(x)
        else:
            return x

    def _getYValue(self, y):
        return str(self.y_format % y)

    def _timestampToDateTime(self, timestamp):
        """
        Method used to caste the timestamp from the curve to date
        in proper format (%Y-%m-%d %H:%M:%S)

        :param timestamp: selected timestamp from curve
        """
        return datetime.utcfromtimestamp(timestamp).strftime(self.date_format)

    def _removeLabels(self):
        # remove existing texts
        for item in self._labels:
            self.getViewBox().removeItem(item)
        self._labels = []
        # remove existing highlights
        self._highlights.setData(pos=())

    def attachToPlotItem(self, plot_item):
        """
        Method to attach :class:`DataInspectorLine` to the plot

        :param plot: to attach
        """
        self._plot_item = plot_item
        self._plot_item.addItem(self, ignoreBounds=True)
        self._plot_item.addItem(self._highlights, ignoreBounds=True)

    def dettach(self):
        """
        Method use to detach the class:`DataInspectorLine` from the plot
        """
        self._removeLabels()
        self._plot_item.removeItem(self._highlights)
        self._plot_item.removeItem(self)
        self._plot_item = None


class DataInspectorTool(Qt.QWidgetAction, BaseConfigurableClass):
    """
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached. When activated, the data inspection mode is
    entered (a :class:`DataInspectorLine` is added and it follows the mouse,
    allowing the user to inspect the coordinates of existing curves).
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    """

    def __init__(self, parent=None):
        BaseConfigurableClass.__init__(self)
        Qt.QWidgetAction.__init__(self, parent)
        self._cb = Qt.QCheckBox()
        self._cb.setText("Data Inspector")
        self._cb.toggled.connect(self._onToggled)
        self.setDefaultWidget(self._cb)

        self.plot_item = None
        self.enable = False
        self.data_inspector = DataInspectorLine()

        self.registerConfigProperty(self.isChecked, self.setChecked, "checked")

    def attachToPlotItem(self, plot_item):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        :param y2: (Y2ViewBox) instance of the Y2Viewbox attached to plot_item
                   if the axis change controls are to be used
        """
        self.plot_item = plot_item
        menu = plot_item.getViewBox().menu
        menu.addAction(self)

    def _onToggled(self):

        if not self.enable:
            self.data_inspector.attachToPlotItem(self.plot_item)
            # Signal Proxy which connect the movement of the mouse with
            # the onMoved method in the data inspector object
            self.proxy = SignalProxy(
                self.plot_item.scene().sigMouseMoved,
                rateLimit=60,
                slot=self._followMouse,
            )
            self.enable = True
            # auto-close the menu so that the user can start inspecting
            self.plot_item.getViewBox().menu.close()

        else:
            self.proxy.disconnect()
            self.data_inspector.dettach()
            self.enable = False

    def _followMouse(self, evt):
        mouse_pos = evt[0]
        inspector_x = self.plot_item.vb.mapSceneToView(mouse_pos).x()
        self.data_inspector.setPos(inspector_x)


if __name__ == "__main__":
    from taurus.qt.qtgui.application import TaurusApplication
    import pyqtgraph as pg
    import sys

    app = TaurusApplication()

    w = pg.PlotWidget(title="[hint: enable inspector mode from context menu]")

    w.plot(y=numpy.arange(4), pen="r", symbol="o")
    w.plot(y=numpy.random.rand(4), pen="c")
    w.plot(
        x=numpy.linspace(0, 3, 40),
        y=1 + numpy.random.rand(40),
        pen="w",
        symbol="+",
    )

    t = DataInspectorTool(w)
    t.attachToPlotItem(w.getPlotItem())

    w.show()
    sys.exit(app.exec_())
