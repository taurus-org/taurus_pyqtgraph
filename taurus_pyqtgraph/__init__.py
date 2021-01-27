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

"""Top-level package for taurus_pyqtgraph."""

from __future__ import absolute_import
import taurus.external.qt as _  # avoid API1 errors due to pyqtgraph imports
from .y2axis import Y2ViewBox, set_y_axis_for_curve
from .curvespropertiestool import CurvesPropertiesTool
from .dateaxisitem import DateAxisItem
from .autopantool import XAutoPanTool
from .plot import TaurusPlot
from .trend import TaurusTrend
from .legendtool import PlotLegendTool
from .forcedreadtool import ForcedReadTool
from .buffersizetool import BufferSizeTool
from .taurusimageitem import TaurusImageItem
from .taurusplotdataitem import TaurusPlotDataItem
from .taurustrendset import TaurusTrendSet, TrendCurve
from .curvesmodel import TaurusItemConf, TaurusItemConfDlg
from .taurusmodelchoosertool import (
    TaurusModelChooserTool,
    TaurusImgModelChooserTool,
    TaurusXYModelChooserTool,
)
from .curveproperties import (
    CurveAppearanceProperties,
    CurvesAppearanceChooser,
    serialize_opts,
    deserialize_opts,
)
from .datainspectortool import DataInspectorLine, DataInspectorTool
from .util import unique_data_item_name, ensure_unique_curve_name

# Do not modify the __version__ manually. To be modified by bumpversion
__version__ = "0.4.10"
