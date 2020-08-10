# taurus_pyqtgraph

`taurus_pyqtgraph` is an extension package for the [Taurus] package. It
adds the `taurus.qt.qtgui.tpg` submodule which provides [pyqtgraph]-based 
widgets.
The rationale behind taurus_pyqtgraph is described in the [TEP17]

## Install

Just install this module e.g.:

For the latest release in PyPI:

`pip install taurus_pyqtgraph`

Alternatively, you can install with conda:

`conda install -c taurus-org taurus_pyqtgraph`

For development, use a python3 virtual env (or conda, or similar) and:

```
git clone https://github.com/taurus-org/taurus_pyqtgraph.git
cd taurus_pyqtgraph
pip install -r requirements_dev.txt -r requirements.txt
pip install -e .
```

After successful installation, the module will be accessible as `taurus.qt.qtgui.tpg` 
and `taurus_tpg`, and `tpg` will be registered as an alternative implementation for 
plots and trends in the `taurus` CLI.

## Features implementation checklist

`taurus_pyqtgraph` is still in alpha stage. Its API may be subject to 
change before the 1.0.0 release.

This is a list of planned / done features. The tasks which are checked are 
those for which there is already an alpha-quality prototype:

### For 1D plots

- [x] 1D plot: plot of multiple 1D models with auto-changing color and
    availability of legend 
- [x] Date-time support on X axis (display only, see "UI for
    setting scale limits *in date/time format*" below) 
- [x] Stand-alone widget
- [x] Zooming & panning with "restore original view" option (not the same
    as zoom stacking, see below)
- [x] Possibility to use (at least) 2 Y-scales
- [x] UI for adding taurus curves via ModelChooser. See also
    "Improved Model Chooser" below 
- [x] Store/retreive configuration (save/load settings)
- [x] Support for non-taurus curves in same plot (aka "raw data")
- [x] UI for setting scale limits and lin/log options 
- [x] Export data as ascii: without date-time support
- [x] Export plot as image (S0)
- [x] UI for moving a curve from one Y-scale to another
- [x] UI for choosing line color, thickness symbol, filling...
- [x] Arbitrary Label scale (aka FixedLabelsScale)
- [ ] configurable properties support (setting permanence)

Outside TEP17 scope:

- [ ] UI for setting scale limits *in date/time format* (S16)
- [x] Point-picking (aka "inspect mode") (S4)
- [ ] Date-time support in "export data as ascii" (S24)
- [ ] Plot freeze (pause) (S8)
- [x] Improved Model Chooser: replacement of the "input data selection"
  dialog allowing to choose *both* X and Y models (see curve selection
  dialog in extra_guiqwt's tauruscurve) (C16)
- [x] Drop support for taurus attributes (C4)
- [ ] Zoom stack: possibility of stacking zoom levels and navigating back 
  one level at a time. (C16)
- [ ] Cursor position info (display X-Y position of cursor in active axis
  coords) (C2)
- [ ] 1D ROI selector (C2)
- [ ] Curve statistics calculator (mean, stdev...) as in curve stats
  dialog of TaurusPlot/Trend (C8)
- [ ] UI for changing curve names (C8)
- [ ] Peak locator: Visual label min/max of curves (C12)
- [ ] UI for adding raw data (W8)
  
### For 1D trends

Most of the features mentioned for 1D plots affect the 1D trends as
well. Apart from those, here is a list of more specific features of
trends:

- [x] "1D trends": plot of scalars vs event number or timestamp
- [x] Fixed-range scale (aka oscilloscope mode)
- [x] UI to switch between fixed and free scale mode
- [x] Stand-alone Widget 
- [x] Support for forced-reading of attributes (aka "-r mode") 
- [x] UI for forced-reading mode
- [ ] configurable properties support (setting permanence)

Outside TEP17 scope:

- [x] "Trend sets": plot of 1D attribute vs time interpreting it as a set
  of 1D scalars (M16)
- [x] Accessing Archived values (M40). Done via [taurus_tangoarchiving plugin]
- [ ] Accessing Tango Polling buffer (W24)
- [x] Support for limiting curve buffers (C8)
- [ ] UI for curve buffers (C2)


### For 2D plots (images)


Outside TEP17 scope:
- [x] Plot a single image 
- [x] UI for Add/remove image
- [ ] Stand-alone Widget (M8)
- [ ] "calibrated" XYImage (assigning values to X and Y scale, as in
    guiqwt's XYImageItem) S8
- [ ] Cross sections (slicing) (S4)
- [ ] 2D ROI Selector (S4)
- [x] LUT/contrast control (S0)
- [ ] Drop support for taurus attributes (C4)
- [ ] LogZ scale (C?)
- [ ] Annotation/measure tools (C16)


### For 2D trends (spectrograms)

Most of the features for 2D plots affect also the 2D trends. Apart
from those, here is a list of more specific features of 2D trends:

Outside TEP17 scope:
- [ ] Stand-alone Widget (M8)
- [ ] Absolute date-time scale (display, see same feat in TaurusPlot)
- [ ] Fixed-range scale (aka oscilloscope mode, same as for 1Dtrends) (M8)
- [ ] UI to switch between fixed and free scale mode (S12)


### In general:
- [ ] Document all public API
- [x] Make all code pep8-clean


[Taurus]: http://taurus-scada.org
[pyqtgraph]: http://pyqtgraph.org
[TEP17]: https://github.com/taurus-org/taurus/pull/452
[taurus_tangoarchiving plugin]: https://github.com/taurus-org/taurus_tangoarchiving
