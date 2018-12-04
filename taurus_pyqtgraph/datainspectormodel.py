from datetime import datetime
import numpy as np

from pyqtgraph import TextItem, InfiniteLine
from dateaxisitem import DateAxisItem


class DataInspectorModel(InfiniteLine):
    """
    DataInspectorModel is a general class use to point-picking.
    This class use a numpy library to finding the nearest point.
    Attach :class:`pyqtgraph.TextItem` widget to the plot -
    to showing the x,y value of the selected point.
    Also this class blink the selected scatter point item.
    """

    def __init__(self, y_format="%0.4f", trigger_point_size=20):
        super(DataInspectorModel, self).__init__(angle=90, movable=True)
        self._labels = []
        self._plot_item = None

        self.y_format = y_format
        self.trigger_point_size = trigger_point_size
        self.date_format = "%Y-%m-%d %H:%M:%S"
        self.cloud_style = "background-color: #35393C;"

    def onMoved(self, evt):
        """
        Slot use to handle the mouse move event, and preform the action
        on the plot.

        :param evt: mouse event
        """

        pos = evt[0]
        x_px_size, _ = self.getViewBox().viewPixelSize()
        inspector_x = self._plot_item.vb.mapSceneToView(pos).x()

        self._removeLabels()
        points = []
        # iterate over the existing curves
        for c in self._plot_item.curves:

            if c.xData is not None:
                # find the index of the closest point of this curve
                adiff = np.abs(c.xData - inspector_x)
                idx = np.argmin(adiff)

                # only add a label if the line touches the symbol
                tolerance = .5 * max(1, c.opts['symbolSize']) * x_px_size
                if adiff[idx] < tolerance:
                    points.append((c.xData[idx], c.yData[idx]))
                    self._triggerPoint(c, idx)
                else:
                    # Clean the trigger points
                    c.updateItems()

                self.setPos(inspector_x)
                self._createLabels(c, points)

    def _createLabels(self, curves, points):
        for x, y in points:
            _x = self._getXValue(x)
            _y = self._getYValue(y)
            text_item = TextItem()
            text_item.setPos(x, y)
            text_item.setHtml("<div style='%s'> "
                              "<span>x=%s "
                              "<span>y=%s</span> "
                              "</div>" % (self.cloud_style, _x, _y))
            self._labels.append(text_item)
            text_item.setParentItem(curves)

    def _triggerPoint(self, c, idx):

        # Update items to make sure that all points have default size
        c.updateItems()

        scatter_point = c.scatter.points()
        if len(scatter_point) > 0:
            scatter_point[idx].setSize(self.trigger_point_size)

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

    def attachToPlotItem(self, plot):
        """
        Method to attach :class:`DataInspectorModel` to the plot

        :param plot: to attach
        """
        self._plot_item = plot
        self._plot_item.addItem(self, ignoreBounds=True)

    def dettach(self):
        """
        Method use to detach the class:`DataInspectorModel` from the plot
        """
        self._removeLabels()
        self._plot_item.removeItem(self)
        self._plot_item = None
