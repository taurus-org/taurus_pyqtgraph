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

"""Example on using a tpg.TaurusPlotDataItem on a pure pyqtgraph plot"""

if __name__ == "__main__":
    import sys
    import numpy
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.tpg import TaurusPlotDataItem
    import pyqtgraph as pg

    app = TaurusApplication()

    # a standard pyqtgraph plot_item
    w = pg.PlotWidget()

    # add legend to the plot, for that we have to give a name to plot items
    w.addLegend()

    # add a regular data item (non-taurus)
    c1 = pg.PlotDataItem(name="pg item", pen="b", fillLevel=0, brush="c")
    c1.setData(numpy.linspace(0, 2, 250))
    w.addItem(c1)

    # add a taurus data item
    c2 = TaurusPlotDataItem(name="taurus item", pen="r", symbol="o")
    c2.setModel('eval:Quantity(rand(256),"m")')
    w.addItem(c2)

    w.show()

    sys.exit(app.exec_())
