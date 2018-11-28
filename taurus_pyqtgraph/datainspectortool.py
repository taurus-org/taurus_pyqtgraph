from taurus.external.qt import QtGui

from pyqtgraph import SignalProxy
from taurus.qt.qtcore.configuration import BaseConfigurableClass

from datainspectormodel import DataInspectorModel


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
        self.data_inspector = None

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
            self.dataInspector = DataInspectorModel(self.plot_item)
            # Signal Proxy which connect the movement of the mouse with
            # the mosueMove method in the data inspector object
            self.proxy = SignalProxy(self.plot_item.scene().sigMouseMoved,
                                     rateLimit=60,
                                     slot=self.dataInspector.mouseMoved)
            self.enable = True

        else:
            self.proxy.disconnect()
            self.dataInspector = None
            self.enable = False


if __name__ == '__main__':
    from trend import TaurusTrendMain
    TaurusTrendMain()
