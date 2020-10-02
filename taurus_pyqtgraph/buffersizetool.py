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
__all__ = ["BufferSizeTool"]

from taurus.external.qt import QtGui, QtCore
from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


class BufferSizeTool(QtGui.QAction, BaseConfigurableClass):
    """
    This tool provides a menu option to control the "Maximum buffer" of
    Plot data items that implement a `setBufferSize` method
    (see, e.g. :meth:`TaurusTrendSet.setBufferSize`).

    This tool inserts an action with a spinbox and emits a `valueChanged`
    signal whenever the value is changed.

    The connection between the data items and this tool can be done manually
    (by connecting to the `valueChanged` signal or automatically, if
    :meth:`autoconnect()` is `True` (default). The autoconnection feature works
    by discovering the compliant data items that are associated to the
    plot_item.

    This tool is implemented as an Action, and provides a method to attach it
    to a :class:`pyqtgraph.PlotItem`
    """

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(
        self,
        parent=None,
        buffer_size=65536,
        text="Change buffers size...",
        autoconnect=True,
    ):
        BaseConfigurableClass.__init__(self)
        QtGui.QAction.__init__(self, text, parent)
        self.setToolTip("Maximum number of points for each trend")
        self._maxSize = buffer_size
        self._autoconnect = autoconnect

        # register config properties
        self.registerConfigProperty(
            self.bufferSize, self.setBufferSize, "buffer_size"
        )
        self.registerConfigProperty(
            self.autoconnect, self.setAutoconnect, "autoconnect"
        )

        # internal conections
        self.triggered.connect(self._onTriggered)

    def _onEdittingFinished(self):
        """
        emit valueChanged and update all associated trendsets (if
        self.autoconnect=True
        """
        buffer_size = self.bufferSize()
        self.valueChanged.emit(buffer_size)
        if self.autoconnect() and self.plot_item is not None:
            for item in self.plot_item.listDataItems():
                if hasattr(item, "setBufferSize"):
                    item.setBufferSize(buffer_size)

    def _onTriggered(self):
        maxSize = self.bufferSize()
        maxSize, ok = QtGui.QInputDialog.getInt(
            self.parentWidget(),
            "New buffer data size",
            "Enter the number of points to be kept in memory for each curve",
            maxSize,
            2,
            10000000,
            1000,
        )
        if ok:
            self.setBufferSize(maxSize)

    def attachToPlotItem(self, plot_item):
        """Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        menu = plot_item.getViewBox().menu
        menu.addAction(self)
        self.plot_item = plot_item
        # ensure that current items are set to max size
        self.setBufferSize(self.bufferSize())
        if self.autoconnect():
            # enable the buffer limit also for trendsets added in the future
            try:  # requires https://github.com/pyqtgraph/pyqtgraph/pull/1388
                plot_item.scene().sigItemAdded.connect(self._onAddedItem)
            except AttributeError:
                pass

    def _onAddedItem(self, item):
        if hasattr(item, "setBufferSize"):
            item.setBufferSize(self.bufferSize())

    def autoconnect(self):
        """Returns autoconnect state

        :return: (bool)
        """
        return self._autoconnect

    def setAutoconnect(self, autoconnect):
        """Set autoconnect state. If True, the tool will autodetect trendsets
        associated to the plot item and will call setBufferSize
        on each of them for each change. If False, it will only emit a
        valueChanged signal and only those connected to it will be notified
        of changes

        :param autoconnect: (bool)
        """
        self._autoconnect = autoconnect

    def bufferSize(self):
        """Returns the current buffer_size value

        :return: (int)
        """
        return self._maxSize

    def setBufferSize(self, buffer_size):
        """Change the buffer_size value.

        :param buffer_size: (int) buffer_size
        """
        self._maxSize = buffer_size
        # update existing items
        if self.autoconnect() and self.plot_item is not None:
            for item in self.plot_item.listDataItems():
                if hasattr(item, "setBufferSize"):
                    item.setBufferSize(buffer_size)
        # emit a valueChanged signal
        self.valueChanged.emit(buffer_size)


if __name__ == "__main__":
    import taurus

    # taurus.setLogLevel(taurus.Debug)
    taurus.changeDefaultPollingPeriod(333)

    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusTrendSet, DateAxisItem
    import pyqtgraph as pg

    # from taurus.qt.qtgui.tpg import MaxBufferTool

    app = TaurusApplication()

    w = pg.PlotWidget()

    axis = DateAxisItem(orientation="bottom")
    w = pg.PlotWidget()
    axis.attachToPlotItem(w.getPlotItem())

    # test adding the curve before the tool
    ts1 = TaurusTrendSet(name="before", symbol="o")
    ts1.setModel("eval:rand()+1")

    w.addItem(ts1)

    fr = BufferSizeTool(w, buffer_size=16)
    fr.attachToPlotItem(w.getPlotItem())

    # test adding the curve after the tool
    ts2 = TaurusTrendSet(name="after", symbol="+")
    ts2.setModel("eval:rand()")

    w.addItem(ts2)

    w.show()

    ret = app.exec_()

    import pprint

    pprint.pprint(fr.createConfig())

    sys.exit(ret)
