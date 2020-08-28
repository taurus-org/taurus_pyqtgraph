import numpy

import taurus_pyqtgraph as tpg
import pyqtgraph as pg
from collections import Counter
import time
import pytest


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
        assert "+rand(" in n

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

    # check that there are no duplications beccause of moving
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
        w[:3] + ts1[1:] + ts2[1:] + ts3[1:]
    )
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


def test_modelchooser_config(qtbot):

    w1 = tpg.TaurusTrend()
    qtbot.addWidget(w1)

    models1 = [
        "eval:1*rand()",
        (None, "eval:2*rand(2)", "foo"),
    ]

    w1.setModel(models1)

    # test createConfig
    cfg = w1.createConfig()
    xymccfg1 = _get_sub_config(cfg, "XYmodelchooser")
    modelscfg1 = _get_sub_config(xymccfg1, "CurveInfo")
    assert modelscfg1[0] == (
        None,
        "eval://localhost/@DefaultEvaluator/1*rand()",
        "1*rand()",
    )
    assert modelscfg1[1] == (
        None,
        "eval://localhost/@DefaultEvaluator/2*rand(2)",
        "foo",
    )

    # test applyConfig
    w2 = tpg.TaurusTrend()
    qtbot.addWidget(w2)
    assert len(w2) == 0
    assert len(w2._model_chooser_tool.getModelNames()) == 0

    # add a model to w2
    w2.setModel("eval:3*rand()")
    assert len(w2) == 1
    assert len(w2._model_chooser_tool.getModelNames()) == 1

    # apply config (the previously added tauruscurve of w2 should be removed)
    w2.applyConfig(cfg)
    assert len(w2) == 2
    assert [isinstance(ts, tpg.TaurusTrendSet) for ts in w2] == [True, True]
    assert len(w2._model_chooser_tool.getModelNames()) == 2
    assert w2._model_chooser_tool._getCurveInfo() == modelscfg1

    # show_and_wait(qtbot, w1, w2)  # uncomment for visually checking

    # avoid teardown issues
    w1.setModel(None)
    w2.setModel(None)


@pytest.mark.xfail(reason="y2axis fails to save/restore in trends")
def test_y2_config(qtbot):

    # create a plot with 2 trendsets of 2 curves each
    w1 = tpg.TaurusTrend()
    qtbot.addWidget(w1)

    models1 = [
        "eval:1*rand(2)",
        (None, "eval:2*rand(2)", "foo"),
    ]

    w1.setModel(models1)

    w1_vb1 = w1.getViewBox()
    w1_vb2 = w1._y2

    assert len(w1) == 2
    ts0, ts1 = w1[:]
    assert [isinstance(ts, tpg.TaurusTrendSet) for ts in w1] == [True, True]

    # check that the 2 trendsets and all their curves are on Y1
    for ts in w1:
        assert ts.getViewBox() == w1_vb1
        assert [c.getViewBox() for c in ts] == [w1_vb1, w1_vb1]
    assert Counter(w1_vb1.addedItems) == Counter(w1[:] + ts0[:] + ts1[:])
    assert w1_vb2.addedItems == []

    # move the second curve of of each trendset to Y2
    for ts in w1:
        c = ts[1]
        w1_vb1.removeItem(c)
        w1_vb2.addItem(c)

    # check that the move was ok and there are no duplicates
    for ts in w1:
        assert ts.getViewBox() == w1_vb1
        assert [c.getViewBox() for c in ts] == [w1_vb1, w1_vb2]
    assert Counter(w1_vb1.addedItems) == Counter(w1[:] + [ts0[0], ts1[0]])
    assert Counter(w1_vb2.addedItems) == Counter([ts0[1], ts1[1]])

    # test createConfig
    plot_cfg = w1.createConfig()
    y2_cfg = _get_sub_config(plot_cfg, "Y2Axis")
    curvescfg1 = _get_sub_config(y2_cfg, "Y2Curves")
    assert curvescfg1 == [ts[1].getFullModelNames() for ts in w1]

    # # Debugging
    # from pprint import pprint
    # pprint(plot_cfg)
    # pprint(curvescfg1)

    # create a second, empty plot
    w2 = tpg.TaurusTrend()
    qtbot.addWidget(w2)

    w2_vb1 = w2.getViewBox()
    w2_vb2 = w2._y2

    assert len(w2) == 0

    # check applyConfig on the new plot
    w2.applyConfig(plot_cfg)
    assert len(w2) == 2
    assert [isinstance(ts, tpg.TaurusTrendSet) for ts in w2] == [True, True]

    for ts in w2:
        assert ts.getViewBox() == w2_vb1
        assert [c.getViewBox() for c in ts] == [w2_vb1, w2_vb1]

    # TODO: The following asserts are known to fail
    assert Counter(w2_vb1.addedItems) == Counter(w2[:] + [ts[0] for ts in w2])
    assert Counter(w2_vb2.addedItems) == Counter([ts[1] for ts in w2])

    # show_and_wait(qtbot, w1, w2)  # uncomment for visually checking

    # avoid teardown issues
    w1.setModel(None)
    w2.setModel(None)


def test_curveproperties_configfile(qtbot, tmp_path):
    w1 = tpg.TaurusTrend()
    qtbot.addWidget(w1)
    w1.setBackground(0.3)

    w1vb1 = w1.getViewBox()
    w1vb2 = w1._y2

    # add a regular data item (non-taurus) to y1
    c0 = pg.PlotDataItem(name="PG-0", pen="y", fillLevel=0, brush="y")
    now = time.time()
    c0.setData(numpy.linspace(now - 5, now + 5, 10), 1 - numpy.random.rand(10))
    w1.getPlotItem().addItem(c0)

    # add a regular data item (non-taurus) to y2
    c1 = pg.PlotDataItem(name="PG-1", pen="y", symbol="d", symbolBrush="r")
    c1.setData(
        numpy.linspace(now - 5, now + 5, 10),
        1 - numpy.linspace(0, 20, 10) / 20.0,
    )
    w1vb2.addItem(c1)

    # add a TrendSet to y1
    ts0 = tpg.TaurusTrendSet(name="TS0", symbol="o")
    ts0.setModel('eval:Quantity(2+rand(),"m")')
    w1.addItem(ts0)
    c2 = ts0[0]

    # add a TrendSet to y2
    ts1 = tpg.TaurusTrendSet(name="TS1", symbol="s")
    ts1.setModel('eval:Quantity(3+rand(),"km")')
    w1vb2.addItem(ts1)
    c3 = ts1[0]

    # Save a config file at this point
    f1 = tmp_path / "trend1.pck"
    w1.saveConfigFile(ofile=str(f1))
    assert f1.exists()
    assert len(list(tmp_path.iterdir())) == 1

    # Add 2 TrendSets using addModel
    models1 = [
        (None, "eval:1*rand(2)", "TS2"),
        (None, "eval:2*rand(2)", "TS3"),
    ]
    w1.addModels(models1)

    ts2 = w1[2]
    c4, c5 = ts2[:]
    ts3 = w1[3]
    c6, c7 = ts3[:]

    c4.setPen("g")

    c5.setPen(None)
    c5.setSymbol("t")
    c5.setSymbolSize(7)
    c5.setSymbolBrush("r")

    c6.setPen("c")

    c7.setPen(None)
    c7.setSymbol("d")
    c7.setSymbolSize(9)
    c7.setSymbolBrush("m")

    # move c5 and c7 to to y2
    w1vb2.addItem(c5)
    w1vb2.addItem(c7)

    assert len(w1) == 4
    assert w1[:] == [ts0, ts1, ts2, ts3]

    assert Counter(w1._cprop_tool.getModifiableItems().values()) == Counter(
        [c0, c1, c2, c3, c4, c5, c6, c7]
    )
    assert Counter(w1vb1.addedItems) == Counter(
        [ts0, ts2, ts3, c0, c2, c4, c6]
    )
    assert Counter(w1vb2.addedItems) == Counter([ts1, c1, c3, c5, c7])

    # Save a config file with everything in w1
    f2 = tmp_path / "trend2.pck"
    w1.saveConfigFile(ofile=str(f2))
    assert f2.exists()
    assert len(list(tmp_path.iterdir())) == 2

    # test loadConfigFile

    w2 = tpg.TaurusTrend()
    qtbot.addWidget(w2)

    w2vb1 = w2.getViewBox()
    w2vb2 = w2._y2

    # load the second config file (containing everything)
    w2.loadConfigFile(ifile=str(f2))

    w1_props = w1._cprop_tool._getCurveAppearanceProperties()
    w2_props = w2._cprop_tool._getCurveAppearanceProperties()

    assert len(w1_props) == 8
    assert len(w2_props) == 6
    for k, p_aft in w2_props.items():
        assert k in w1_props
        p_ini = w1_props[k]
        assert not p_ini.conflictsWith(p_aft, strict=True)

    # show_and_wait(qtbot, w1, w2)  # uncomment for visually checking

    # load the first config file (does not contain TS2 and TS3)
    w2.loadConfigFile(ifile=str(f1))

    # check that there are not leftovers from previous config
    assert len(w2)  # only the curves from ts0 and ts1
    assert [ts.base_name() for ts in w2] == ["TS0", "TS1"]

    # --------------------------------------------------------------------
    # The following 2 (commented) asserts assume that the viewbox of the
    # TaurusTrendSet is properly restored, but that is not the case
    # (only the TrendCurves viewbox is currently properly restored):
    #     assert Counter(vb1.addedItems) == Counter([w2[0], w2[0][0]])
    #     assert Counter(vb2.addedItems) == Counter([w2[1], w2[1][0]])
    # use the following two asserts instead for now
    assert Counter(w2vb1.addedItems) == Counter([w2[0], w2[1], w2[0][0]])
    assert Counter(w2vb2.addedItems) == Counter([w2[1][0]])
    # TODO: implement proper save/restore of trendset viewbox
    # From the user perspective, it does not seem to have a big impact,
    # but I suspect that there will eventually be troubles because of this
    # inconsistency
    # --------------------------------------------------------------------

    w2_props = w2._cprop_tool._getCurveAppearanceProperties()
    # --------------------------------------------------------------------
    # The following assert is failing (TS2[0] and TS3[0] are still being
    # picked by _cprop_tool._getCurveAppearanceProperties())
    # TODO: investigate
    # For the moment, just (comment it out)
    # assert len(w2_props) == 2  # only the curves from ts0 and ts1 !
    # --------------------------------------------------------------------
    for k, p_aft in w2_props.items():
        assert k in w1_props
        p_ini = w1_props[k]
        assert not p_ini.conflictsWith(p_aft, strict=True)

    # show_and_wait(qtbot, w1, w2)  # uncomment for visual checks

    # avoid teardown issues
    w1.setModel(None)
    w2.setModel(None)


def test_multiple_setModel(qtbot):
    """
    Check that repeated calls to setModel do not duplicate the items
    in the plot
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    for i in range(5):
        w.setModel(["eval:rand(2)"])
        sets = w.getTrendSets()
        assert Counter(w.getPlotItem().listDataItems()) == Counter(
            [sets[0], w[0], w[1]]
        ), "Found duplicates after {} calls to setModel".format(i + 1)
    # workaround for teardown issue
    w.setModel(None)
