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

"""Example on using a tpg.Y2ViewBox to provide a secondary Y axis"""

from PyQt5 import Qt
import pyqtgraph as pg
import numpy
from taurus.qt.qtgui.tpg import Y2ViewBox, CurvesPropertiesTool


if __name__ == "__main__":
    import sys

    app = Qt.QApplication([])

    w = pg.PlotWidget()

    # add Y2 viewbox (provides a ViewBox associated to bottom & right axes)
    y2 = Y2ViewBox()
    y2.attachToPlotItem(w.getPlotItem())

    # add a data item to Y1 (just as you would normally)
    c1 = pg.PlotDataItem(name="c1", pen="c")
    c1.setData(y=numpy.linspace(0, 20, 250))
    w.addItem(c1)

    # add a data item to Y2 (similar, but adding it to the secondary ViewBox!)
    c2 = pg.PlotDataItem(name="c2", pen="y")
    c2.setData(y=numpy.random.rand(250))
    y2.addItem(c2)  # <- note that it is y2, not w !

    # (optional) add CurvesPropertiesTool to switch curves between Y1 and Y2
    t = CurvesPropertiesTool()
    t.attachToPlotItem(w.getPlotItem(), y2=y2)

    w.show()
    sys.exit(app.exec_())
