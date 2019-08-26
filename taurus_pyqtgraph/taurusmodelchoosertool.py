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

__all__ = ["TaurusModelChooserTool", "TaurusImgModelChooserTool"]

from builtins import bytes
from future.utils import string_types

from taurus.external.qt import Qt
from taurus.core import TaurusElementType
from taurus.qt.qtgui.panel import TaurusModelChooser
from taurus_pyqtgraph.taurusimageitem import TaurusImageItem
from taurus_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem
from taurus_pyqtgraph.curvesmodel import TaurusItemConf, TaurusItemConfDlg
import taurus
from collections import OrderedDict
from taurus.qt.qtcore.mimetypes import (
    TAURUS_MODEL_LIST_MIME_TYPE,
    TAURUS_ATTR_MIME_TYPE,
)


class TaurusModelChooserTool(Qt.QAction):
    """
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached to show choosing taurus models to be shown.
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    """

    def __init__(self, parent=None, itemClass=None):
        Qt.QAction.__init__(self, "Model selection", parent)
        self.triggered.connect(self._onTriggered)
        self.plot_item = None
        self.legend = None
        if itemClass is None:
            itemClass = TaurusPlotDataItem
        self.itemClass = itemClass

    def attachToPlotItem(self, plot_item, parentWidget=None):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        self.plot_item = plot_item
        if self.plot_item.legend is not None:
            self.legend = self.plot_item.legend

        menu = self.plot_item.getViewBox().menu
        menu.addAction(self)
        self.setParent(parentWidget or menu)

    def _onTriggered(self):
        currentModelNames = []
        for item in self.plot_item.items:
            if isinstance(item, self.itemClass):
                currentModelNames.append(item.getFullModelName())
        names, ok = TaurusModelChooser.modelChooserDlg(
            selectables=[TaurusElementType.Attribute],
            listedModels=currentModelNames,
        )
        if ok:
            self.updateModels(names)

    def updateModels(self, names):
        """Accepts a list of model names and updates the data items of class
        `itemClass` (provided in the constructor) attached to the plot.
        It creates and removes items if needed, and enforces the z-order
        according to that given in the `models` list
        """
        # from names, construct an ordered dict with k=fullname, v=modelObj
        models = OrderedDict()
        for n in names:
            m = taurus.Attribute(n)
            models[m.getFullName()] = m

        # construct a dict and a list for current models and names
        currentModelItems = dict()
        currentModelNames = []
        for item in self.plot_item.items:
            if isinstance(item, self.itemClass):
                fullname = item.getFullModelName()
                currentModelNames.append(fullname)
                currentModelItems[fullname] = item

        # remove existing curves from plot (but not discarding the object)
        # so that they can be re-added later in the correct z-order
        for k, v in currentModelItems.items():
            # v.getViewBox().removeItem(v)  # TODO: maybe needed for Y2
            self.plot_item.removeItem(v)
            # -------------------------------------------------
            # Workaround for bug in pyqtgraph 0.10.0
            # (which is fixed in pyqtgraph's commit ee0ea5669)
            # TODO: remove this lines when pyqtgraph > 0.10.0 is released
            if self.legend is not None:
                self.legend.removeItem(v.name())
            # -------------------------------------------------

        # Add all curves (creating those that did not exist previously)
        # respecting the z-order
        for modelName, model in models.items():
            if modelName in currentModelNames:
                item = currentModelItems[modelName]
                self.plot_item.addItem(item)
                # item.getViewBox().addItem(item)  # TODO: maybe needed for Y2
            else:
                # TODO support labels
                item = self.itemClass(name=model.getSimpleName())
                item.setModel(modelName)
                self.plot_item.addItem(item)

        # self.plot_item.enableAutoRange()  # TODO: Why? remove?

    def setParent(self, parent):
        """Reimplement setParent to add an event filter"""
        Qt.QAction.setParent(self, parent)
        if parent is not None:
            parent.installEventFilter(self)

    def _dropMimeData(self, data):
        """Method to process the dropped MimeData"""
        ymodels = []
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            m = bytes(data.data(TAURUS_ATTR_MIME_TYPE)).decode("utf-8")
            ymodels.append(m)

        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            ymodels = (
                bytes(data.data(TAURUS_MODEL_LIST_MIME_TYPE))
                .decode("utf-8")
                .split()
            )
        elif data.hasText():
            ymodels.append(data.text())

        # Add models
        current = []
        for item in self.plot_item.items:
            if isinstance(item, self.itemClass):
                current.append(item.getFullModelName())
        self.updateModels(current + ymodels)
        return True

    def eventFilter(self, source, event):
        """
        Reimplementation of eventFilter to delegate parent's drag and drop
        events to TaurusModelChooserTool
        """
        if source is self.parent():
            if event.type() == Qt.QEvent.DragEnter:
                event.acceptProposedAction()
                return True

            if event.type() == Qt.QEvent.Drop:
                event.acceptProposedAction()
                return self._dropMimeData(event.mimeData())

        return self.parent().eventFilter(source, event)


class TaurusImgModelChooserTool(Qt.QAction):
    """
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached for choosing a 2D taurus model to be shown.
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    """

    # TODO: merge this with TaurusModelChooserTool (or use a common base)

    def __init__(self, parent=None):
        Qt.QAction.__init__(self, parent)
        self._plot_item = None

    def attachToPlotItem(self, plot_item):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        self._plot_item = plot_item
        view = plot_item.getViewBox()
        menu = view.menu
        model_chooser = Qt.QAction("Model selection", menu)
        model_chooser.triggered.connect(self._onTriggered)
        menu.addAction(model_chooser)

    def _onTriggered(self):

        imageItem = None

        for item in self._plot_item.items:
            if isinstance(item, TaurusImageItem):
                imageItem = item
                break

        if imageItem is None:
            imageItem = TaurusImageItem()
        modelName = imageItem.getFullModelName()
        if modelName is None:
            listedModels = []
        else:
            listedModels = [modelName]

        res, ok = TaurusModelChooser.modelChooserDlg(
            selectables=[TaurusElementType.Attribute],
            singleModel=True,
            listedModels=listedModels,
        )
        if ok:
            if res:
                model = res[0]
            else:
                model = None
            imageItem.setModel(model)


class TaurusXYModelChooserTool(Qt.QAction):
    """
    (Work-in-Progress)
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached for choosing X and Y 1D taurus models of the curves
    to be shown.
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    It only deals with the subgroup of plot data items of the type defined by
    `self.ItemClass` (which defaults to :class:`TaurusPlotDataItem`)
    """

    # TODO: This class is WIP.
    def __init__(self, parent=None, itemClass=None):
        Qt.QAction.__init__(self, "Model selection", parent)
        self.triggered.connect(self._onTriggered)
        self.plot_item = None
        self.legend = None
        self._curveColors = None
        if itemClass is None:
            itemClass = TaurusPlotDataItem
        self.itemClass = itemClass

    def setParent(self, parent):
        """Reimplement setParent to add an event filter"""
        Qt.QAction.setParent(self, parent)
        if parent is not None:
            parent.installEventFilter(self)

    def attachToPlotItem(
        self, plot_item, parentWidget=None, curve_colors=None
    ):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)

        .. warning:: this is Work-in-progress. The API may change.
             Do not rely on current signature of this method
        """
        # TODO: Check if we can simplify the signature (remove keyword args)
        self.plot_item = plot_item
        self._curveColors = curve_colors
        if self.plot_item.legend is not None:
            self.legend = self.plot_item.legend

        menu = self.plot_item.getViewBox().menu
        menu.addAction(self)
        self.setParent(parentWidget or menu)

    def _onTriggered(self):
        oldconfs = self._getTaurusPlotDataItemConfigs().values()
        newconfs, ok = TaurusItemConfDlg.showDlg(
            parent=self.parent(), taurusItemConf=oldconfs
        )

        if ok:
            xy_names = [(c.xModel, c.yModel) for c in newconfs]
            self.updateModels(xy_names)
            # TODO: apply configurations too

    def _getTaurusPlotDataItemConfigs(self):
        """Get all the TaurusItemConf of the existing TaurusPlotDataItems
        Returns an ordered dict whose keys are (xfullname, yfullname)
        and whose values are the corresponding item config class
        """
        itemconfigs = OrderedDict()
        for curve in self.plot_item.listDataItems():
            if isinstance(curve, self.itemClass):
                xmodel, ymodel = curve.getFullModelNames()
                c = TaurusItemConf(
                    YModel=ymodel, XModel=xmodel, name=curve.name()
                )
                itemconfigs[(xmodel, ymodel)] = c
        return itemconfigs

    def _dropMimeData(self, data):
        """Method to process the dropped MimeData"""
        ymodels = []
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            m = bytes(data.data(TAURUS_ATTR_MIME_TYPE)).decode("utf-8")
            ymodels.append(m)

        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            ymodels = (
                bytes(data.data(TAURUS_MODEL_LIST_MIME_TYPE))
                .decode("utf-8")
                .split()
            )
        elif data.hasText():
            ymodels.append(data.text())

        xmodels = [None] * len(ymodels)
        self.addModels(list(zip(xmodels, ymodels)))
        return True

    def eventFilter(self, source, event):
        """
        Reimplementation of eventFilter to delegate parent's drag and drop
        events to TaurusXYModelChooserTool
        """
        if source is self.parent():
            if event.type() == Qt.QEvent.DragEnter:
                event.acceptProposedAction()
                return True

            if event.type() == Qt.QEvent.Drop:
                event.acceptProposedAction()
                return self._dropMimeData(event.mimeData())

        return self.parent().eventFilter(source, event)

    def getModelNames(self):
        """
        Get the x and y model names for the data items of type
        defined by `self.itemClass` present in the plot item to which
        this tool is attached
        """
        return list(self._getTaurusPlotDataItemConfigs().keys())

    def addModels(self, xy_names):
        """Add new items with the given x and y model pairs. Those given model
        pairs that are already present will not be altered or duplicated (e.g.
        the z-order of the corresponding curve will not be modified for in case
        of adding duplicates)
        """
        current = self.getModelNames()
        self.updateModels(current + xy_names)

    def updateModels(self, xy_names):
        """
        Update the current plot item list with the given configuration items
        """
        mainViewBox = self.plot_item.getViewBox()
        # Remove existing taurus curves from the plot (but keep the item object
        # and a reference to their viewbox so that they can be readded
        # later on if needed.
        currentModelItems = OrderedDict()
        _currentCurves = list(self.plot_item.listDataItems())
        for curve in _currentCurves:
            if isinstance(curve, self.itemClass):
                xname, yname = curve.getFullModelNames()
                viewbox = curve.getViewBox()
                # store curve and current viewbox for later use
                currentModelItems[(xname, yname)] = curve, viewbox
                # remove the curve
                self.plot_item.removeItem(curve)
                # if viewbox is not mainViewBox:  # TODO: do we need this?
                #     viewbox.removeItem(curve)
                if self.legend is not None:
                    self.legend.removeItem(curve.name())

        # Add only the curves defined in xy_names (reusing existing ones and
        # creating those that did not exist) in the desired z-order
        _already_added = []
        for xy_name in xy_names:
            # each member of xy_names can be yname or a (xname, yname) tuple
            if isinstance(xy_name, string_types):
                xname, yname = None, xy_name
            else:
                xname, yname = xy_name
            # make sure that fullnames are used
            try:
                if xname is not None:
                    xmodel = taurus.Attribute(xname)
                    xname = xmodel.getFullName()
                ymodel = taurus.Attribute(yname)
                yname = ymodel.getFullName()
            except Exception as e:
                from taurus import warning

                warning("Problem adding %r: %r", (xname, yname), e)
                continue
            # do not add it again if we already added it (avoid duplications)
            if (xname, yname) in _already_added:
                continue
            _already_added.append((xname, yname))
            # if the item already existed, re-use it
            if (xname, yname) in currentModelItems:
                item, viewbox = currentModelItems[(xname, yname)]
                self.plot_item.addItem(item)
                if viewbox is not mainViewBox:
                    # if the curve was originally associated to a viewbox
                    # other than the main one, we should move it there after
                    # re-adding it to the plot_item
                    mainViewBox.removeItem(item)
                    viewbox.addItem(item)
            # if it is a new curve, create it and add it to the main plot_item
            else:
                item = self.itemClass(
                    xModel=xname, yModel=yname, name=ymodel.getSimpleName()
                )
                if self._curveColors is not None:
                    item.setPen(self._curveColors.next().color())
                self.plot_item.addItem(item)


def _demo_ModelChooser():
    import sys
    import numpy
    import pyqtgraph as pg
    from taurus.qt.qtgui.tpg import TaurusModelChooserTool
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusPlotDataItem

    app = TaurusApplication()

    # a standard pyqtgraph plot_item
    w = pg.PlotWidget()

    # add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name="st plot", pen="b", fillLevel=0, brush="c")
    c1.setData(numpy.arange(300) / 300.0)
    w.addItem(c1)

    # adding a taurus data item
    c2 = TaurusPlotDataItem(name="st2 plot", pen="r", symbol="o")
    c2.setModel("eval:rand(222)")

    w.addItem(c2)

    # attach to plot item
    tool = TaurusModelChooserTool(itemClass=TaurusPlotDataItem)
    tool.attachToPlotItem(w.getPlotItem())

    w.show()

    tool.trigger()

    sys.exit(app.exec_())


def _demo_ModelChooserImage():
    import sys
    from taurus.qt.qtgui.tpg import TaurusImgModelChooserTool, TaurusImageItem
    from taurus.qt.qtgui.application import TaurusApplication
    import pyqtgraph as pg

    app = TaurusApplication()

    w = pg.PlotWidget()

    img = TaurusImageItem()

    # Add taurus 2D image data
    img.setModel("eval:rand(256,256)")

    w.addItem(img)

    w.showAxis("left", show=False)
    w.showAxis("bottom", show=False)

    tool = TaurusImgModelChooserTool()
    tool.attachToPlotItem(w.getPlotItem())

    w.show()

    tool.trigger()
    sys.exit(app.exec_())


if __name__ == "__main__":
    _demo_ModelChooser()
    # _demo_ModelChooserImage()
