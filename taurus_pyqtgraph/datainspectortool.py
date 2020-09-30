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
from pyqtgraph import SignalProxy, InfiniteLine, TextItem, PlotDataItem


class DataInspectorLine(InfiniteLine):
    """
    DataInspectorLine provides a moveable vertical line item that shows labels
    containing the coordinates of the points of existing curves it touches.
    It provides a method to attach it to a PlotItem.

    """

    # TODO: modify anchor of labels so that they are plotted on the left if
    #       they do not fit in the view

    def __init__(
        self,
        date_format="%Y-%m-%d %H:%M:%S",
        x_format="0.4f",
        y_format="0.4f",
        trigger_point_size=10,
    ):
        """

        :param date_format: format string (as in strftime) for displaying dates
        :param x_format: format specifier for displaying the x values
        :param y_format: format specifier for displaying the y values
        :param trigger_point_size: width (in pixels) of the inspected area
                                   (points will be picked only if they are
                                   within this size)
        """
        super(DataInspectorLine, self).__init__(angle=90, movable=True)
        self._labels = []
        self._highlights = []
        self._plot_item = None

        self._date_format = "{:" + date_format + "}"
        self._x_format = "{:" + x_format + "}"
        self._y_format = "{:" + y_format + "}"
        self.trigger_point_size = trigger_point_size
        self._label_style = "background-color: #35393C;"
        self.sigPositionChanged.connect(self._inspect)

    def _inspect(self):
        """
        check if the line position matches (in widget coordinates) the position
        of a point of a given curve. If so, add a highlight point and a label
        in the corresponding viewbox.
        """
        # remove labels (text and highlight points)
        self._removeLabels()
        # group curves to be inspected, by their viewbox
        vb_curves = {}
        for c in self._plot_item.curves:
            if getattr(c, "xData", None) is not None:
                vb = c.getViewBox()
                if vb not in vb_curves:
                    vb_curves[vb] = []
                vb_curves[vb].append(c)

        # inspect the curves of each viewbox
        for vb, curves in vb_curves.items():
            self._inspect_curves_in_viewbox(curves, vb)

    def _inspect_curves_in_viewbox(self, curves, viewbox):

        # map position of the line to the viewbox coordinates
        xpos = viewbox.mapFromItemToView(self, self.pos()).x()
        # find out the screen pixel size in the viewbox coordinates
        x_px_size, _ = viewbox.viewPixelSize()

        points = []  # picked points, grouped by their viewbox
        # iterate over the curves
        for c in curves:
            # find the index of the closest point of this curve
            adiff = numpy.abs(c.xData - xpos)
            idx = numpy.argmin(adiff)
            # only add a label if the closest point is within tolerance
            tolerance = 0.5 * self.trigger_point_size * x_px_size
            if adiff[idx] < tolerance:
                points.append((c.xData[idx], c.yData[idx]))

        if curves:
            logMode = curves[0].opts["logMode"]
        else:
            logMode = None
        self._createLabels(points, viewbox, logMode)

    def _createLabels(self, points, viewbox, logMode):
        for x, y in points:
            # fill the text
            xtext = self._getXText(x)
            ytext = self._getYText(y)
            text_item = TextItem()
            text_item.setHtml(
                (
                    "<div style='{}'> "
                    + "<span><b>x=</b>{} "
                    + "<span><b>y=</b>{}</span> "
                    + "</div>"
                ).format(self._label_style, xtext, ytext)
            )
            # add text_item in the right position (take into account log mode)
            if logMode[0]:
                x = numpy.log10(x)
            if logMode[1]:
                y = numpy.log10(y)
            text_item.setPos(x, y)
            self._labels.append(text_item)
            viewbox.addItem(text_item, ignoreBounds=True)
        # Add "highlight" marker at each point
        highlight = PlotDataItem(
            numpy.array(points),
            pen=None,
            symbol="s",
            symbolBrush="35393C88",
            pxMode=True,
            symbolSize=self.trigger_point_size,
        )
        # set log mode
        highlight.setLogMode(*logMode)
        # hack to make the CurvesPropertiesTool ignore the highlight points
        highlight._UImodifiable = False
        # Add it to the vbox and keep a reference
        viewbox.addItem(highlight, ignoreBounds=True)
        self._highlights.append(highlight)

    def _getXText(self, x):
        """
        Helper method converting x value to time if necessary

        :param x: current x value
        :return: time or normal x value (depends of the x axis type)
        """
        x_axis = self._plot_item.getAxis("bottom")
        if isinstance(x_axis, DateAxisItem):
            return self._date_format.format(datetime.utcfromtimestamp(x))
        else:
            return self._x_format.format(x)

    def _getYText(self, y):
        return self._y_format.format(y)

    def _removeLabels(self):
        # remove existing texts labels and highlights
        for item in self._labels + self._highlights:
            item.getViewBox().removeItem(item)
        self._labels = []
        self._highlights = []

    def attachToPlotItem(self, plot_item):
        """
        Method to attach :class:`DataInspectorLine` to the plot

        :param plot: to attach
        """
        self._plot_item = plot_item
        self._plot_item.addItem(self, ignoreBounds=True)

    def dettach(self):
        """
        Method use to detach the class:`DataInspectorLine` from the plot
        """
        self._removeLabels()
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
