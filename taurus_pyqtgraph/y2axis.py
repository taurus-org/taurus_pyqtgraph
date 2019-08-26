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

__all__ = ["Y2ViewBox"]


from pyqtgraph import ViewBox, PlotItem

from taurus.qt.qtcore.configuration.configuration import BaseConfigurableClass


def _PlotItem_addItem(self, item, *args, **kwargs):
    """replacement for `PlotItem.addItem` that Y2Axis will use to monkey-patch
    the original one
    """
    PlotItem.addItem(self, item, *args, **kwargs)

    if hasattr(item, "setLogMode"):
        item.setLogMode(
            self.getAxis("bottom").logMode, self.getAxis("left").logMode
        )


class Y2ViewBox(ViewBox, BaseConfigurableClass):
    """
    A tool that inserts a secondary Y axis to a plot item (see
    :meth:`attachToPlotItem`).
    It is implemented as a :class:`pyqtgraph.ViewBox` and provides methods to
    add and remove :class:`pyqtgraph.PlotDataItem` objects to it.
    """

    def __init__(self, *args, **kwargs):
        BaseConfigurableClass.__init__(self)
        ViewBox.__init__(self, *args, **kwargs)

        self.registerConfigProperty(self.getCurves, self.setCurves, "Y2Curves")
        self.registerConfigProperty(self._getState, self.setState, "viewState")
        self._isAttached = False
        self.plotItem = None
        self._curvesModelNames = []

    def attachToPlotItem(self, plot_item):
        """Use this method to add this axis to a plot

        :param plot_item: (PlotItem)
        """
        if self._isAttached:
            return  # TODO: log a message it's already attached
        self._isAttached = True

        mainViewBox = plot_item.getViewBox()
        mainViewBox.sigResized.connect(self._updateViews)

        self.plotItem = plot_item

        # add axis-independent actions for logarithmic scale
        self._addLogAxisActions()
        # disable the standard (custom view-unfriendly) log actions
        self.plotItem.ctrl.logXCheck.setEnabled(False)
        self.plotItem.ctrl.logYCheck.setEnabled(False)

        # monkey-patch the addItem method of the PlotItem
        from types import MethodType

        self.plotItem.addItem = MethodType(_PlotItem_addItem, self.plotItem)

    def _updateViews(self, viewBox):
        self.setGeometry(viewBox.sceneBoundingRect())
        self.linkedViewChanged(viewBox, self.XAxis)

    def removeItem(self, item):
        """Reimplemented from :class:`pyqtgraph.ViewBox`"""
        ViewBox.removeItem(self, item)

        # when last curve is removed from self (axis Y2), we must remove the
        # axis from scene and hide the axis.
        if len(self.addedItems) < 1:
            self.plotItem.scene().removeItem(self)
            self.plotItem.hideAxis("right")

        if hasattr(item, "getFullModelNames"):
            self._curvesModelNames.remove(item.getFullModelNames())

    def addItem(self, item, ignoreBounds=False):
        """Reimplemented from :class:`pyqtgraph.ViewBox`"""
        ViewBox.addItem(self, item, ignoreBounds=ignoreBounds)

        if len(self.addedItems) == 1:
            # when the first curve is added to self (axis Y2), we must
            # add Y2 to main scene(), show the axis and link X axis to self.
            self.plotItem.showAxis("right")
            self.plotItem.scene().addItem(self)
            self.plotItem.getAxis("right").linkToView(self)
            self.setXLink(self.plotItem)

        # set the item log mode to match this view:
        if hasattr(item, "setLogMode"):
            item.setLogMode(
                self.plotItem.getAxis("bottom").logMode,
                self.plotItem.getAxis("right").logMode,
            )

        if hasattr(item, "getFullModelNames") and (
            len(self.addedItems) > 0
            and item.getFullModelNames() not in self._curvesModelNames
        ):
            self._curvesModelNames.append(item.getFullModelNames())

    def getCurves(self):
        """Returns the curve model names of curves associated to the Y2 axis.

        :return: (list) List of tuples of model names (xModelName, yModelName)
                 from each curve in this view
        """
        return self._curvesModelNames

    def setCurves(self, curves):
        """Sets the curve names associated to the Y2 axis (but does not
        create/remove any curve.
        """
        self._curvesModelNames = curves

    def _getState(self):
        """Same as ViewBox.getState but removing viewRange conf to force
        a refresh with targetRange when loading
        """
        state = self.getState(copy=True)
        del state["viewRange"]
        return state

    def clearItems(self):
        """Remove the added items"""
        for c in self.addedItems:
            self.removeItem(c)

    def _addLogAxisActions(self):
        # insert & connect actions Log Scale Actions
        # X (bottom)
        menu = self.plotItem.getViewBox().menu.axes[0]
        action = menu.addAction("Log scale")
        action.setCheckable(True)
        action.setChecked(self.plotItem.getAxis("bottom").logMode)
        action.setParent(menu)
        action.toggled.connect(self._onXLogToggled)
        self.menu.axes[0].addAction(action)  # Add same action to X2 menu too
        # Y1 (left)
        menu = self.plotItem.getViewBox().menu.axes[1]
        action = menu.addAction("Log scale")
        action.setCheckable(True)
        action.setChecked(self.plotItem.getAxis("left").logMode)
        action.setParent(menu)
        action.toggled.connect(self._onY1LogToggled)
        # Y2 (right)
        menu = self.menu.axes[1]
        action = menu.addAction("Log scale")
        action.setCheckable(True)
        action.setChecked(self.plotItem.getAxis("right").logMode)
        action.setParent(menu)
        action.toggled.connect(self._onY2LogToggled)

    def _onXLogToggled(self, checked):
        logx = checked

        # set log mode for items of main viewbox
        logy = self.plotItem.getAxis("left").logMode
        for i in self.plotItem.getViewBox().addedItems:
            if hasattr(i, "setLogMode"):
                i.setLogMode(logx, logy)
        # set log mode for items of Y2 viewbox
        logy = self.plotItem.getAxis("right").logMode
        for i in self.addedItems:
            if hasattr(i, "setLogMode"):
                i.setLogMode(logx, logy)
        # set log mode for the bottom axis
        self.plotItem.getAxis("bottom").setLogMode(checked)

    def _onY1LogToggled(self, checked):
        # set log mode for items of main viewbox
        logx = self.plotItem.getAxis("bottom").logMode
        logy = checked
        for i in self.plotItem.getViewBox().addedItems:
            if hasattr(i, "setLogMode"):
                i.setLogMode(logx, logy)
        # set log mode for the left axis
        self.plotItem.getAxis("left").setLogMode(checked)

    def _onY2LogToggled(self, checked):
        # set log mode for items of Y2 viewbox
        logx = self.plotItem.getAxis("bottom").logMode
        logy = checked
        for i in self.addedItems:
            if hasattr(i, "setLogMode"):
                i.setLogMode(logx, logy)
        # set log mode for the right axis
        self.plotItem.getAxis("right").setLogMode(checked)
