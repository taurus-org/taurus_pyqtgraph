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
import numpy as np

from pyqtgraph import TextItem, InfiniteLine, ScatterPlotItem
from taurus_pyqtgraph.dateaxisitem import DateAxisItem


class DataInspectorLine(InfiniteLine):
    """
    DataInspectorLine is a general class use to point-picking.
    This class use a numpy library to finding the nearest point.
    Attach :class:`pyqtgraph.TextItem` widget to the plot -
    to showing the x,y value of the selected point.
    Also this class blink the selected scatter point item.
    """

    #TODO: support more than 1 viewbox (e.g. y2axis).

    def __init__(self, date_format="%Y-%m-%d %H:%M:%S", y_format="%0.4f",
                 trigger_point_size=10):
        super(DataInspectorLine, self).__init__(angle=90, movable=True)
        self._labels = []
        self._plot_item = None

        self.y_format = y_format
        self.trigger_point_size = trigger_point_size
        self.date_format = date_format
        self._label_style = "background-color: #35393C;"
        self.sigPositionChanged.connect(self._inspect)
        self._highlights = ScatterPlotItem(
            pos=(), symbol='s', brush="35393C88", pxMode=True,
            size=trigger_point_size
        )
        # hack to make the curvespropertiestool ignore the highlights item
        self._highlights._UImodifiable = False

    def _inspect(self):
        """
        Slot to re inspector line movemethe mouse move event, and peform the action
        on the plot.

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
                adiff = np.abs(c.xData - xpos)
                idx = np.argmin(adiff)
                # only add a label if the line touches the symbol
                tolerance = .5 * max(1, c.opts['symbolSize']) * x_px_size
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
            text_item.setHtml(("<div style='{}'> "
                               + "<span><b>x=</b>{} "
                               + "<span><b>y=</b>{}</span> "
                               + "</div>").format(self._label_style, _x, _y)
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
