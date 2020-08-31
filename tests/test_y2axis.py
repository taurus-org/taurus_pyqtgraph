import taurus_pyqtgraph as tpg
from .test_trend import show_and_wait  # noqa


def test_y2legend(qtbot):
    """
    Check that legend items are not duplicated or lost on changes of Y axis
    """
    w = tpg.TaurusPlot()
    qtbot.addWidget(w)

    vb1 = w.getViewBox()
    vb2 = w._y2
    plot_item = w.getPlotItem()
    legend = plot_item.legend
    assert w[:] == []
    assert vb1.addedItems == []
    assert vb2.addedItems == []
    assert legend.items == []

    # Add a curve to Y1
    w.setModel([(None, "eval:1*rand(11)", "foo")])
    c = w[0]
    assert w[:] == [c]
    assert vb1.addedItems == [c]
    assert vb2.addedItems == []
    assert len(legend.items) == 1
    assert legend.items[0][1].text == "foo"

    # move c to Y2
    tpg.set_y_axis_for_curve(
        y2=True, dataItem=c, plotItem=plot_item, y2Axis=w._y2
    )
    assert w[:] == [c]
    assert vb1.addedItems == []
    assert vb2.addedItems == [c]
    assert len(legend.items) == 1
    assert legend.items[0][1].text == "foo"

    # move c back to Y1
    tpg.set_y_axis_for_curve(
        y2=False, dataItem=c, plotItem=plot_item, y2Axis=w._y2
    )
    assert w[:] == [c]
    assert vb1.addedItems == [c]
    assert vb2.addedItems == []
    assert len(legend.items) == 1
    assert legend.items[0][1].text == "foo"
