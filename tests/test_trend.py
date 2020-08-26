import numpy

import taurus
taurus.changeDefaultPollingPeriod(333)
import taurus_pyqtgraph as tpg
import pyqtgraph as pg
from collections import Counter
import time


def _get_sub_config(cfg, item):
    assert item in cfg["__itemConfigurations__"]
    assert item in cfg["__orderedConfigNames__"]
    return cfg["__itemConfigurations__"][item]


def show_and_wait(qtbot, *widgets, timeout=60000, raising=False):
    """
    Helper that shows widgets and waits until they are closed (or timeout ms)
    """
    for w in widgets:
        w.show()
    def are_closed():
        for w in widgets:
            if w.isVisible():
                return False
        return True
    try:
        qtbot.wait_until(are_closed, timeout=timeout)
    except AssertionError:
        if raising:
            raise

# def test_trend_teardown(qtbot):
#     """
#     For some reason (to be investigated) the teardown of this tests
#     triggers a crash in pytest (maybe related to qt?)
#     """
#     w = tpg.TaurusTrend()
#     qtbot.addWidget(w)
#     m = ["eval:1", "eval:2"]
#     # m = ["eval:1", "eval:2"]  # uncommenting this line avoids the trigger
#     # m = ["eval:1", "eval:2"]  # uncommenting this line avoids the trigger
#     w.setModel(m)
#     # w.setModel([])  # uncommenting this line avoids the trigger


def test_trend_model_setting(qtbot):

    w = tpg.TaurusTrend()
    qtbot.addWidget(w)

    vb1 = w.getViewBox()
    vb2 = w._y2

    assert len(w) == 0
    assert w[:] == []
    assert w._model_chooser_tool.getModelNames() == []
    assert vb1.addedItems == []
    assert vb2.addedItems == []

    models = [
        "eval:1+rand()",
        "eval:2+rand(2)",
        "eval:3+rand(3)",
    ]

    w.setModel(models)
    ts0 = w[0]
    ts1 = w[1]
    ts2 = w[2]

    assert len(w) == 3
    assert len(ts0) == 1
    assert len(ts1) == 2
    assert len(ts2) == 3
    assert len(w._model_chooser_tool._getCurveInfo()) == 3

    for m, (x, y, n) in zip(models, w._model_chooser_tool._getCurveInfo()):
        assert x is None
        assert y.endswith(m[5:])
        assert n is None

    assert ts0[0].name() == "1+rand()[0]"
    assert ts1[0].name() == "2+rand(2)[0]"
    assert ts1[1].name() == "2+rand(2)[1]"
    assert ts2[0].name() == "3+rand(3)[0]"
    assert ts2[1].name() == "3+rand(3)[1]"
    assert ts2[2].name() == "3+rand(3)[2]"

    assert w._model_chooser_tool.getModelNames() == [
        ts.getFullModelNames() for ts in w[:]
    ]

    # check items of viewboxes (for vb1, ignore the sorting)
    assert Counter(vb1.addedItems) == Counter(w[:] + ts0[:] + ts1[:] + ts2[:])
    assert vb2.addedItems == []

    # move the whole ts1 to Y2
    # vb1.removeItem(ts1)
    # vb2.addItem(ts1)  # TODO: NOT WORKING (crashes!)
    # assert Counter(vb1.addedItems) == Counter([ts0, ts2] + ts0[:] + ts2[:])
    # assert Counter(vb1.addedItems) == Counter([ts1] + ts1[:])

    # move first curve of each trendset to Y2
    for ts in w:
        c = ts[0]
        vb1.removeItem(c)
        vb2.addItem(c)
    assert Counter(vb1.addedItems) == Counter(w[:] + ts1[1:] + ts2[1:])
    assert vb2.addedItems == [ts0[0], ts1[0], ts2[0]]

    #check that there are no duplications beccause of moving
    assert len(w) == 3
    assert len(ts0) == 1
    assert len(ts1) == 2
    assert len(ts2) == 3
    assert len(w._model_chooser_tool._getCurveInfo()) == 3

    # add a regular data item (non-taurus) to y2
    c0 = pg.PlotDataItem(name="pg item", pen="y", fillLevel=0, brush="y")
    now = time.time()
    c0.setData(numpy.linspace(now - 5, now + 5, 10), 1 - numpy.random.rand(10))
    vb2.addItem(c0)

    # check that the regular item is not counted as a trendset item...
    assert w[:] == [ts0, ts1, ts2]
    assert w._model_chooser_tool.getModelNames() == [
        ts.getFullModelNames() for ts in w[:]
    ]
    # ... but still, it is added to y2
    assert Counter(vb1.addedItems) == Counter(w[:] + ts1[1:] + ts2[1:])
    assert vb2.addedItems == [ts0[0], ts1[0], ts2[0], c0]

    # manually add a trendset to y2
    ts3 = tpg.TaurusTrendSet(name="TS-3", symbol="o")
    ts3.setModel('eval:Quantity(rand(2)-1,"m")')
    vb2.addItem(ts3)

    assert len(ts3) == 2
    assert w[:] == [ts0, ts1, ts2, ts3]
    assert Counter(vb1.addedItems) == Counter(w[:3] + ts1[1:] + ts2[1:])
    assert Counter(vb2.addedItems) == Counter(
        [ts0[0], ts1[0], ts2[0], c0, ts3] + ts3[:]
    )
    assert w._model_chooser_tool.getModelNames() == [
        ts0.getFullModelNames(),
        ts1.getFullModelNames(),
        ts2.getFullModelNames(),
        ts3.getFullModelNames(),
    ]

    # move the second curve of ts3 to y1 and check that all is as expected
    c = ts3[1]
    vb2.removeItem(c)
    vb1.addItem(c)

    assert len(ts3) == 2
    assert w[:] == [ts0, ts1, ts2, ts3]
    assert Counter(vb1.addedItems) == Counter(
        w[:3] + ts1[1:] + ts2[1:] + ts3[1:])
    assert Counter(vb2.addedItems) == Counter(
        [ts0[0], ts1[0], ts2[0], ts3[0], c0, ts3]
    )

    # manually add a trendset to y1
    ts4 = tpg.TaurusTrendSet(name="TS-4", symbol="s")
    ts4.setModel('eval:Quantity(rand()-2,"m")')
    w.addItem(ts4)

    assert len(ts4) == 1
    assert w[:] == [ts0, ts1, ts2, ts3, ts4]
    assert Counter(vb1.addedItems) == Counter(
        [ts0, ts1, ts2, ts4] + ts1[1:] + ts2[1:] + ts3[1:] + ts4[:]
    )
    assert Counter(vb2.addedItems) == Counter(
        [ts0[0], ts1[0], ts2[0], c0, ts3, ts3[0]]
    )
    assert w._model_chooser_tool.getModelNames() == [
        ts0.getFullModelNames(),
        ts1.getFullModelNames(),
        ts2.getFullModelNames(),
        ts3.getFullModelNames(),
        ts4.getFullModelNames(),
    ]

    # show_and_wait(qtbot, w)  # uncomment for visually checking

    # Add existing (ts1) model again and check that nothing is recreated
    ts0_0 = ts0[0]
    ts1_0, ts1_1 = ts1[:]
    ts2_0, ts2_1, ts2_2 = ts2[:]
    ts3_0, ts3_1 = ts3[:]
    ts4_0 = ts4[0]

    w.addModels([models[1]])

    assert w[:] == [ts0, ts1, ts2, ts3, ts4]
    assert w[0][:] == [ts0_0]
    assert w[1][:] == [ts1_0, ts1_1]
    assert w[2][:] == [ts2_0, ts2_1, ts2_2]
    assert w[3][:] == [ts3_0, ts3_1]
    assert w[4][:] == [ts4_0]

    # -----------------------------------------------------------------------
    # nothing is recreated or duplicated, but all the trendsets are reset
    # and their curves restored to the trendset viewbox even if they had
    # been moved to another one.
    # TODO: check if we want to avoid that and have the following instead
    # assert Counter(vb1.addedItems) == Counter(
    #     [ts0, ts1, ts2, ts4] + ts1[1:] + ts2[1:] + ts3[1:] + ts4[:]
    # )
    # assert Counter(vb2.addedItems) == Counter(
    #     [ts0[0], ts1[0], ts2[0], c0, ts3, ts3[0]]
    # )
    # -----------------------------------------------------------------------
    assert Counter(vb1.addedItems) == Counter(
        [ts0, ts1, ts2, ts4] + ts0[:] + ts1[:] + ts2[:] + ts4[:]
    )
    assert Counter(vb2.addedItems) == Counter([c0, ts3] + ts3[:])
    assert w._model_chooser_tool.getModelNames() == [
        ts0.getFullModelNames(),
        ts1.getFullModelNames(),
        ts2.getFullModelNames(),
        ts3.getFullModelNames(),
        ts4.getFullModelNames(),
    ]

    # set (not adding!) 1 model which is already on y1
    # only the non-taurus curve and the just set trendset remain.
    w.setModel([models[1]])
    assert w[:] == [ts1]  # ts1 **is** still the same object!
    assert Counter(vb1.addedItems) == Counter([ts1] + ts1[:])
    assert vb2.addedItems == [c0]
    assert w._model_chooser_tool.getModelNames() == [ts1.getFullModelNames()]

    # set empty model (not adding!, the non taurus curve is kept)
    w.setModel([])
    assert w[:] == []
    assert vb1.addedItems == []
    assert vb2.addedItems == [c0]
    assert w._model_chooser_tool.getModelNames() == []

    # show_and_wait(qtbot, w)  # uncomment for visually checking

    # remove non-taurus curve
    vb2.removeItem(c0)
    assert w[:] == []
    assert vb1.addedItems == []
    assert vb2.addedItems == []
    assert w._model_chooser_tool.getModelNames() == []

    # show_and_wait(qtbot, w)  # uncomment for visually checking
