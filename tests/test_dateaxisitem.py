from taurus.external.qt import Qt
import taurus_pyqtgraph as tpg


def test_tickValues(qtbot):
    """
    Check that the tickValues reimplementation returns the expected values
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    a = w.getPlotItem().axes["bottom"]["item"]
    # check return values in the minutes scale
    assert a.tickValues(-65, 125, 1e3)[0] == (60.0, [-60.0, 0.0, 60.0, 120.0])
    # check that the datetime overflows do not break the call
    assert a.tickValues(-1e19, 0, 1e3) == [(1e19, [])]
    assert a.tickValues(0, 1e19, 1e3) == [(1e19, [])]


def test_tickStrings(qtbot):
    """
    Check that the tickStrings reimplementation returns the expected values
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    a = w.getPlotItem().axes["bottom"]["item"]
    # check return values in the minutes scale
    assert a.tickStrings([-60.0, 120.0], None, 60) == ["00:59", "01:02"]
