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

from taurus.external.qt import QtGui

from pyqtgraph import SignalProxy
from taurus.qt.qtcore.configuration import BaseConfigurableClass

from taurus_pyqtgraph.datainspectorline import DataInspectorLine


class DataInspectorTool(QtGui.QWidgetAction, BaseConfigurableClass):
    """
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached to show a :class:'QtGui.QCheckBox' which is use to
    enable the datainspector mode.
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    """

    def __init__(self, parent=None):
        QtGui.QWidgetAction.__init__(self, parent)
        self._cb = QtGui.QCheckBox()
        self._cb.setText('Data Inspector')
        self._cb.toggled.connect(self._onToggled)
        self.setDefaultWidget(self._cb)

        self.plot_item = None
        self.enable = False
        self.data_inspector = DataInspectorLine()

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
            self.proxy = SignalProxy(self.plot_item.scene().sigMouseMoved,
                                     rateLimit=60,
                                     slot=self._followMouse)
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


if __name__ == '__main__':
    from trend import TaurusTrendMain
    TaurusTrendMain()
