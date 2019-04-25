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

from taurus.external.qt import Qt
from taurus.core import TaurusElementType
from taurus.qt.qtgui.panel import TaurusModelChooser
from taurus_pyqtgraph.taurusimageitem import TaurusImageItem
from taurus_pyqtgraph.taurusplotdataitem import TaurusPlotDataItem
from taurus_pyqtgraph.curvesmodel import TaurusItemConf, TaurusItemConfDlg
import taurus
from collections import OrderedDict
from taurus.core.taurushelper import getValidatorFromName
from taurus.qt.qtcore.mimetypes import (TAURUS_MODEL_LIST_MIME_TYPE,
                                        TAURUS_ATTR_MIME_TYPE)


class TaurusModelChooserTool(Qt.QAction):
    """
    This tool inserts an action in the menu of the :class:`pyqtgraph.PlotItem`
    to which it is attached to show choosing taurus models to be shown.
    It is implemented as an Action, and provides a method to attach it to a
    PlotItem.
    """
    def __init__(self, parent=None, itemClass=None):
        Qt.QAction.__init__(self, 'Model chooser', parent)
        self.triggered.connect(self._onTriggered)
        self.plot_item = None
        self.legend = None
        if itemClass is None:
            itemClass = TaurusPlotDataItem
        self.itemClass = itemClass

    def attachToPlotItem(self, plot_item):
        """
        Use this method to add this tool to a plot

        :param plot_item: (PlotItem)
        """
        self.plot_item = plot_item
        if self.plot_item.legend is not None:
            self.legend = self.plot_item.legend

        menu = self.plot_item.getViewBox().menu
        menu.addAction(self)

    def _onTriggered(self):
        currentModelNames = []
        for item in self.plot_item.items:
            if isinstance(item, self.itemClass):
                currentModelNames.append(item.getFullModelName())
        names, ok = TaurusModelChooser.modelChooserDlg(
                    selectables=[TaurusElementType.Attribute],
                    listedModels=currentModelNames)
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
            # v.getViewBox().removeItem(v)  # TODO : maybe this is needed forY2
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
                # item.getViewBox().addItem(item)  # TODO : maybe this is needed forY2
            else:
                # TODO support labels
                item = self.itemClass(name=model.getSimpleName())
                item.setModel(modelName)
                self.plot_item.addItem(item)

        # self.plot_item.enableAutoRange()  # TODO: Why? remove?


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
        model_chooser = Qt.QAction('Model chooser', menu)
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
                    singleModel=True, listedModels=listedModels)
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
    """

    # TODO: This class is WIP.
    def __init__(self, parent=None):
        Qt.QAction.__init__(self, 'Model XY chooser', parent)
        self.triggered.connect(self._onTriggered)
        self.plot_item = None
        self.legend = None
        self._curveColors = None

    def setParent(self, parent):
        """Reimplement setParent to add an event filter"""
        Qt.QAction.setParent(self, parent)
        if parent is not None:
            parent.installEventFilter(self)

    def attachToPlotItem(self, plot_item,
                         parentWidget=None, curve_colors=None):
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
        itemsconf = self.getTaurusPlotDataItemsConf()
        conf, ok = TaurusItemConfDlg.showDlg(
            parent=self.parent(), taurusItemConf=itemsconf)

        if ok:
            self.updatePlotItems(conf)

    def getTaurusPlotDataItemsConf(self):
        """Get all the TaurusItemConf of the existing TaurusPlotDataItems"""
        items = []
        for curve in self.plot_item.listDataItems():
            if isinstance(curve, TaurusPlotDataItem):
                xmodel, ymodel = curve.getFullModelNames()
                items.append(TaurusItemConf(YModel=ymodel, XModel=xmodel,
                                            name=curve.name()))
        return items

    def dropMimeData(self, data):
        """Method to process the dropped MimeData"""
        models = []
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            m = bytes(data.data(TAURUS_ATTR_MIME_TYPE)).decode("utf-8")
            models.append(m)

        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            models = bytes(data.data(TAURUS_MODEL_LIST_MIME_TYPE)
                           ).decode("utf-8").split()
        elif data.hasText():
            models.append(data.text())

        if len(models) > 0:
            conf_list = self.getTaurusPlotDataItemsConf()
            for model in models:
                v = getValidatorFromName(model)
                _, _, simple_name = v.getNames(model)
                # TODO fill XModel maybe using validator?
                conf_list.append(TaurusItemConf(YModel=model, XModel=None,
                                                name=simple_name))
            self.updatePlotItems(conf_list)
            return True
        return False

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
                return self.dropMimeData(event.mimeData())

        return self.parent().eventFilter(source, event)

    def updatePlotItems(self, conf_items):
        """
        Update the current plot item list with the given configuration items
        """
        currentModelItems = {}
        currentModelNames = []

        for curve in self.plot_item.listDataItems():
            if isinstance(curve, TaurusPlotDataItem):
                xmodel, ymodel = curve.getFullModelNames()
                currentModelNames.append((xmodel, ymodel))
                currentModelItems[(xmodel, ymodel)] = curve, curve.getViewBox()

        yModels = OrderedDict()
        xModels = OrderedDict()
        curve_name = OrderedDict()
        for conf in conf_items:
            try:
                m = taurus.Attribute(conf.yModel)
                n = conf.xModel
                name = conf.curveLabel
                yModels[n, m.getFullName()] = m
                xModels[n, m.getFullName()] = n
                curve_name[n, m.getFullName()] = name
            except Exception as e:
                from taurus import warning
                warning(e)

            for k, v in currentModelItems.items():
                curve, parent = v
                self.plot_item.removeItem(curve)
                parent.removeItem(curve)
                if self.legend is not None:
                    self.legend.removeItem(curve.name())

            for modelName, model in yModels.items():
                # print modelName, model
                if modelName in currentModelNames:
                    item, parent = currentModelItems[modelName]
                    X = xModels[modelName]
                    c_name = curve_name[modelName]
                    item.opts['name'] = c_name
                    item.setXModel(X)
                    self.plot_item.addItem(item)

                    # checks if the viewBox associated to
                    # TaurusPlotDataItem(curve), it is the main view or not.
                    # If is the same, we dont have to addItem again in the
                    # parent (viewBox). This avoid duplicate objects in the
                    # ViewBox.scene() contained in PlotItem.
                    if parent is not self.plot_item.getViewBox():
                        parent.addItem(item)

                elif modelName not in currentModelNames:
                    x_model = xModels[modelName]
                    y_model = yModels[modelName]
                    c_name = curve_name[modelName]
                    item = TaurusPlotDataItem(
                        xModel=x_model, yModel=y_model, name=c_name)

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

    #add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # adding a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name='st plot', pen='b', fillLevel=0, brush='c')
    c1.setData(numpy.arange(300) / 300.)
    w.addItem(c1)

    # adding a taurus data item
    c2 = TaurusPlotDataItem(name='st2 plot', pen='r', symbol='o')
    c2.setModel('eval:rand(222)')

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
    img.setModel('eval:rand(256,256)')

    w.addItem(img)

    w.showAxis('left', show=False)
    w.showAxis('bottom', show=False)

    tool = TaurusImgModelChooserTool()
    tool.attachToPlotItem(w.getPlotItem())

    w.show()

    tool.trigger()
    sys.exit(app.exec_())


if __name__ == '__main__':
    _demo_ModelChooser()
    # _demo_ModelChooserImage()

