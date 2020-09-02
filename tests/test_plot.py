import sys
import pytest
import numpy
import taurus_pyqtgraph as tpg
import pyqtgraph as pg
from taurus.external.qt import Qt

from .util import show_and_wait, get_sub_config  # noqa


def test_plot_model_setting(qtbot):

    w = tpg.TaurusPlot()
    qtbot.addWidget(w)

    assert len(w) == 0
    assert len(w._model_chooser_tool.getModelNames()) == 0

    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]

    w.setModel(models1)
    c0 = w[0]
    c1 = w[1]
    assert len(w) == 2
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
    ]

    # add a regular data item (non-taurus)
    c2 = pg.PlotDataItem(name="pg item", pen="b", fillLevel=0, brush="c")
    c2.setData(numpy.linspace(0, 20, 10))
    w.addItem(c2)
    assert w[:] == [c0, c1, c2]
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
    ]

    # add a taurus data item
    c3 = tpg.TaurusPlotDataItem(name="taurus item", pen="r", symbol="o")
    c3.setModel('eval:Quantity(rand(16),"m")')
    w.addItem(c3)
    assert w[:] == [c0, c1, c2, c3]
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
        c3.getFullModelNames(),
    ]

    # Add existing (c0) model again (it is ignored)
    w.addModels([models1[0]])
    assert w[:] == [c2, c0, c1, c3]  # there is reordering, non taurus first
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
        c3.getFullModelNames(),
    ]

    # set 1 model (not adding!, the non-taurus curve is kept)
    w.setModel([models1[1]])
    assert w[:] == [c2, c1]  # c1 **is** still the same object!
    assert w._model_chooser_tool.getModelNames() == [c1.getFullModelNames()]

    # set empty model (not adding!, the non taurus curve is kept)
    w.setModel([])
    assert w[:] == [c2]
    assert w._model_chooser_tool.getModelNames() == []

    # remove non-taurus curve
    w.removeItem(c2)
    assert w[:] == []
    assert w._model_chooser_tool.getModelNames() == []

    # Uncomment for visual checks
    # show_and_wait(qtbot, w, timeout=3600000)


def test_plot_model_setting_with_y2(qtbot):

    w = tpg.TaurusPlot()
    qtbot.addWidget(w)
    vb1 = w.getViewBox()
    vb2 = w._y2

    assert w[:] == []
    assert w._model_chooser_tool.getModelNames() == []
    assert vb1.addedItems == []
    assert vb2.addedItems == []

    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]

    w.setModel(models1)
    c0 = w[0]
    c1 = w[1]

    # move the first curve to Y2
    vb1.removeItem(c0)
    vb2.addItem(c0)
    assert vb1.addedItems == [c1]
    assert vb2.addedItems == [c0]

    assert w[:] == [c0, c1]
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
    ]

    # add a regular data item (non-taurus) to y2
    c2 = pg.PlotDataItem(name="pg item", pen="b", fillLevel=0, brush="c")
    c2.setData(numpy.linspace(0, 20, 10))
    vb2.addItem(c2)

    assert vb1.addedItems == [c1]
    assert vb2.addedItems == [c0, c2]

    assert len(w) == 3
    assert w[:] == [c0, c1, c2]
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
    ]

    # add a taurus data item to y2
    c3 = tpg.TaurusPlotDataItem(name="taurus item", pen="r", symbol="o")
    c3.setModel('eval:Quantity(rand(16),"m")')
    vb2.addItem(c3)
    assert vb1.addedItems == [c1]
    assert vb2.addedItems == [c0, c2, c3]
    assert w[:] == [c0, c1, c2, c3]
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
        c3.getFullModelNames(),
    ]

    # Add existing (c0) model again
    w.addModels([models1[0]])
    assert vb1.addedItems == [c1]
    assert vb2.addedItems == [c2, c0, c3]
    assert w[:] == [c2, c0, c1, c3]  # there is reordering, non taurus first
    assert w._model_chooser_tool.getModelNames() == [
        c0.getFullModelNames(),
        c1.getFullModelNames(),
        c3.getFullModelNames(),
    ]

    # set (not adding!) 1 model which is already on y2
    # only non-taurus curve and the set curve remain. Both stay in y2
    w.setModel([models1[0]])
    assert vb1.addedItems == []
    assert vb2.addedItems == [c2, c0]
    assert w[:] == [c2, c0]  # c0 **is** still the same object!
    assert w._model_chooser_tool.getModelNames() == [c0.getFullModelNames()]

    # set empty model (not adding!, only the non-taurus curve remains)
    w.setModel([])
    assert vb1.addedItems == []
    assert vb2.addedItems == [c2]
    assert w[:] == [c2]
    assert w._model_chooser_tool.getModelNames() == []

    # remove non-taurus curve
    c2.getViewBox().removeItem(c2)
    w.getPlotItem().removeItem(c2)
    assert vb1.addedItems == []
    assert vb2.addedItems == []
    assert w[:] == []
    assert w._model_chooser_tool.getModelNames() == []

    # Uncomment for visual checks
    # show_and_wait(qtbot, w, timeout=3600000)


def test_multiple_setModel(qtbot):
    """
    Check that repeated calls to setModel do not duplicate the items
    in the plot
    """
    w = tpg.TaurusPlot()
    qtbot.addWidget(w)
    for i in range(5):
        w.setModel(["eval:rand(2)"])
        assert w.getPlotItem().listDataItems() == [
            w[0]
        ], "Found duplicates after {} calls to setModel".format(i + 1)


def test_xymodelchooser_config(qtbot):

    w1 = tpg.TaurusPlot()
    qtbot.addWidget(w1)

    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]

    w1.setModel(models1)

    # test createConfig
    cfg = w1.createConfig()
    xymccfg1 = get_sub_config(cfg, "XYmodelchooser")
    modelscfg1 = get_sub_config(xymccfg1, "CurveInfo")
    assert modelscfg1[0] == (
        None,
        "eval://localhost/@DefaultEvaluator/1*rand(22)",
        "1*rand(22)",
    )
    assert modelscfg1[1] == (
        "eval://localhost/@DefaultEvaluator/linspace(-10,20,10)",
        "eval://localhost/@DefaultEvaluator/2*rand(10)",
        "2*rand(10)",
    )

    # test applyConfig
    w2 = tpg.TaurusPlot()
    qtbot.addWidget(w2)
    assert len(w2) == 0
    assert len(w2._model_chooser_tool.getModelNames()) == 0

    # add a model to w2
    w2.setModel("eval:9*rand(11)")
    assert len(w2) == 1
    assert len(w2._model_chooser_tool.getModelNames()) == 1

    # apply config (the previously added tauruscurve of w2 should be removed)
    w2.applyConfig(cfg)
    assert len(w2) == 2
    assert len(w2._model_chooser_tool.getModelNames()) == 2
    assert w2._model_chooser_tool._getCurveInfo() == modelscfg1

    # Uncomment for visual checks
    # show_and_wait(qtbot, w1, w2, timeout=3600000)


def test_y2_config(qtbot):

    # create a plot with 3 curves
    w1 = tpg.TaurusPlot()
    qtbot.addWidget(w1)

    models1 = [
        "eval:1*rand(11)",
        "eval:2*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]

    w1.setModel(models1)

    w1_vb1 = w1.getViewBox()
    w1_vb2 = w1._y2

    # check that the 3 curves are on Y1
    assert [c.getViewBox() for c in w1] == [w1_vb1] * 3
    assert len(w1_vb1.addedItems) == 3
    assert len(w1_vb2.addedItems) == 0

    # move the second curve to Y2
    c = w1[1]
    w1_vb1.removeItem(c)
    w1_vb2.addItem(c)

    # check that the move was ok and there are no duplicates
    assert [c.getViewBox() for c in w1] == [w1_vb1, w1_vb2, w1_vb1]
    assert w1_vb2._getCurvesNames() == [w1[1].getFullModelNames()]
    assert len(w1_vb1.addedItems) == 2
    assert len(w1_vb2.addedItems) == 1

    # test createConfig
    plot_cfg = w1.createConfig()
    y2_cfg = get_sub_config(plot_cfg, "Y2Axis")
    curvescfg1 = get_sub_config(y2_cfg, "Y2Curves")
    assert curvescfg1 == [w1[1].getFullModelNames()]

    # # Debugging
    # from pprint import pprint
    # pprint(plot_cfg)
    # pprint(curvescfg1)

    # create a second, empty plot
    w2 = tpg.TaurusPlot()
    qtbot.addWidget(w2)
    assert len(w2) == 0

    # check applyConfig on the new plot
    w2.applyConfig(plot_cfg)
    assert len(w2) == 3

    w2_vb1 = w2.getViewBox()
    w2_vb2 = w2._y2
    w1_all_names = [c.getFullModelNames() for c in w1]
    w2_all_names = [c.getFullModelNames() for c in w2]

    assert w1_all_names == w2_all_names
    assert len(w2_all_names) == 3
    assert len(w2_vb1.addedItems) == 2
    assert len(w2_vb2.addedItems) == 1
    assert w2_vb2._getCurvesNames() == w1_vb2._getCurvesNames()
    assert w2_vb2._getCurvesNames() == [w1[1].getFullModelNames()]

    # Uncomment for visual checks
    # show_and_wait(qtbot, w1, w2, timeout=3600000)


def test_curveproperties(qtbot):

    w = tpg.TaurusPlot()
    qtbot.addWidget(w)

    # add a regular data item (non-taurus) to y1
    c0 = pg.PlotDataItem(name="pg item1", pen="b", fillLevel=0, brush="c")
    c0.setData(numpy.linspace(0, 20, 10))
    w.addItem(c0)

    # add a regular data item (non-taurus) to y2
    c1 = pg.PlotDataItem(name="pg item2", pen="y", symbol="d", symbolBrush="r")
    c1.setData(20 - numpy.linspace(0, 20, 10))
    w._y2.addItem(c1)

    # add a taurus data item to y1
    c2 = tpg.TaurusPlotDataItem(name="taurus item1", pen="r", symbol="o")
    c2.setModel('eval:Quantity(rand(16),"m")')
    w.addItem(c2)

    # add a taurus data item to y2
    c3 = tpg.TaurusPlotDataItem(name="taurus item2", pen="y", symbol="s")
    c3.setModel('eval:Quantity(rand(20),"km")')
    w._y2.addItem(c3)

    # Add 2 more items using setModel
    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]
    w.addModels(models1)
    c4 = w[4]
    c5 = w[5]

    c4.setPen("g")

    c5.setPen(None)
    c5.setSymbol("t")
    c5.setSymbolSize(7)

    # move c5 to y2
    w._y2.addItem(c5)

    assert len(w) == 6
    assert w[:] == [c0, c1, c2, c3, c4, c5]
    assert len(w._cprop_tool.getModifiableItems()) == 6
    for c in [c0, c1, c2, c3, c4, c5]:
        assert c.name() in w._cprop_tool.getModifiableItems().keys()
        assert c in w._cprop_tool.getModifiableItems().values()
    assert w.getViewBox().addedItems == [c0, c2, c4]
    assert w._y2.addedItems == [c1, c3, c5]

    prop = w._cprop_tool._getCurveAppearanceProperties()

    # check lColor
    assert pg.mkColor(prop[c0.name()].lColor) == pg.mkColor("b")
    assert pg.mkColor(prop[c1.name()].lColor) == pg.mkColor("y")
    assert pg.mkColor(prop[c2.name()].lColor) == pg.mkColor("r")
    assert pg.mkColor(prop[c3.name()].lColor) == pg.mkColor("y")
    assert pg.mkColor(prop[c4.name()].lColor) == pg.mkColor("g")
    # assert pg.mkColor(prop[c5.name()].lColor) == pg.mkColor('b')

    # check lStyle
    for c in c0, c1, c2, c3, c4:
        assert prop[c.name()].lStyle == Qt.Qt.SolidLine
    assert prop[c5.name()].lStyle == Qt.Qt.NoPen

    # check y2
    for c in c0, c2, c4:
        assert prop[c.name()].y2 is False
    for c in c1, c3, c5:
        assert prop[c.name()].y2 is True

    # Uncomment for visual checks
    # show_and_wait(qtbot, w, timeout=3600000)


@pytest.mark.xfail(
    sys.version_info[:2] == (3, 6),
    reason="flaky behaviour observed in CI for py 3.6 in this test",
)
def test_curveproperties_config(qtbot):
    w1 = tpg.TaurusPlot()
    qtbot.addWidget(w1)

    # add a regular data item (non-taurus) to y1
    c0 = pg.PlotDataItem(name="pg item1", pen="m", fillLevel=0, brush="c")
    c0.setData(numpy.linspace(0, 20, 10) / 20.0)
    w1.addItem(c0)

    # add a regular data item (non-taurus) to y2
    c1 = pg.PlotDataItem(name="pg item2", pen="y", symbol="d", symbolBrush="r")
    c1.setData(1 - numpy.linspace(0, 20, 10) / 20.0)
    w1._y2.addItem(c1)

    # add a taurus data item to y1
    c2 = tpg.TaurusPlotDataItem(name="taurus item1", pen="r", symbol="o")
    c2.setModel('eval:Quantity(rand(16),"m")')
    w1.addItem(c2)

    # add a taurus data item to y2
    c3 = tpg.TaurusPlotDataItem(name="taurus item2", pen="y", symbol="s")
    c3.setModel('eval:Quantity(rand(20),"km")')
    w1._y2.addItem(c3)

    # Add 2 more items using setModel
    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]
    w1.addModels(models1)
    c4 = w1[4]
    c5 = w1[5]

    c4.setPen("g")

    c5.setPen(None)
    c5.setSymbol("t")
    c5.setSymbolSize(7)
    c5.setSymbolBrush("r")

    # move c5 to y2
    w1._y2.addItem(c5)

    assert len(w1) == 6
    assert w1[:] == [c0, c1, c2, c3, c4, c5]
    w1_mod_items = w1._cprop_tool.getModifiableItems()
    for c in [c0, c1, c2, c3, c4, c5]:
        assert c0 in w1_mod_items.values()
    assert w1.getViewBox().addedItems == [c0, c2, c4]
    assert w1._y2.addedItems == [c1, c3, c5]

    # test createConfig
    cfg = w1.createConfig()
    propcfg = get_sub_config(cfg, "CurvePropertiesTool")
    _ = get_sub_config(propcfg, "CurveProperties")

    # # Debugging
    # from pprint import pprint
    # # pprint(cfg)
    # print("-" * 80)
    # pprint(curvescfg)

    # test applyConfig
    w2 = tpg.TaurusPlot()
    qtbot.addWidget(w2)
    # assert len(w2._model_chooser_tool.getModelNames()) == 0
    assert len(w2._cprop_tool._getCurveAppearanceProperties()) == 0

    w2.applyConfig(cfg)
    # assert len(w2._model_chooser_tool.getModelNames()) == 2
    # assert w2._model_chooser_tool.getModelNames() == modelscfg1

    w1_props = w1._cprop_tool._getCurveAppearanceProperties()
    w2_props = w2._cprop_tool._getCurveAppearanceProperties()

    assert len(w1_props) == 6
    assert len(w2_props) == 4
    for k, p_aft in w2_props.items():
        assert k in w1_props
        p_ini = w1_props[k]
        conflicts = p_ini.conflictsWith(p_aft, strict=True)
        msg = "Mismatch in saved/restored curve properties for '{}':".format(k)
        msg += "\n\t Saved:    {}".format(p_ini)
        msg += "\n\t Restored: {}".format(p_aft)
        assert conflicts == [], msg

    # test applyConfig
    w3 = tpg.TaurusPlot()
    qtbot.addWidget(w3)

    # Manually add regular data items matching the names used in w1
    # but do not match the properties, which should be updated by applyConfig
    c0_w3 = pg.PlotDataItem(
        name="pg item1", y=numpy.linspace(0, 20, 10) / 20.0
    )
    w3.addItem(c0_w3)
    c1_w3 = pg.PlotDataItem(name="pg item2", y=numpy.zeros(15))
    w3._y2.addItem(c1_w3)

    assert len(w3._cprop_tool._getCurveAppearanceProperties()) == 2

    w3.applyConfig(cfg)

    w3_props = w3._cprop_tool._getCurveAppearanceProperties()

    assert len(w3_props) == 6
    for k, p_aft in w3_props.items():
        assert k in w1_props
        p_ini = w1_props[k]
        conflicts = p_ini.conflictsWith(p_aft, strict=True)
        msg = "Mismatch in saved/restored curve properties for '{}':".format(k)
        msg += "\n\t Saved:    {}".format(p_ini)
        msg += "\n\t Restored: {}".format(p_aft)
        assert conflicts == [], msg

    # Uncomment for visual checks
    # show_and_wait(qtbot, w1, w2, w3, timeout=3600000)


def test_curveproperties_configfile(qtbot, tmp_path):
    w1 = tpg.TaurusPlot()
    qtbot.addWidget(w1)
    w1.setBackground("y")

    # add a regular data item (non-taurus) to y1
    c0 = pg.PlotDataItem(name="pg item1", pen="m", fillLevel=0, brush="c")
    c0.setData(numpy.linspace(0, 20, 10) / 20.0)
    w1.addItem(c0)

    # add a regular data item (non-taurus) to y2
    c1 = pg.PlotDataItem(name="pg item2", pen="y", symbol="d", symbolBrush="r")
    c1.setData(1 - numpy.linspace(0, 20, 10) / 20.0)
    w1._y2.addItem(c1)

    # add a taurus data item to y1
    c2 = tpg.TaurusPlotDataItem(name="taurus item1", pen="r", symbol="o")
    c2.setModel('eval:Quantity(rand(16),"m")')
    w1.addItem(c2)

    # add a taurus data item to y2
    c3 = tpg.TaurusPlotDataItem(name="taurus item2", pen="y", symbol="s")
    c3.setModel('eval:Quantity(rand(20),"km")')
    w1._y2.addItem(c3)

    # Add 2 more items using setModel
    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)", "eval:2*rand(10)"),
    ]
    w1.addModels(models1)
    c4 = w1[4]
    c5 = w1[5]

    c4.setPen("g")

    c5.setPen(None)
    c5.setSymbol("t")
    c5.setSymbolSize(7)
    c5.setSymbolBrush("r")

    # move c5 to y2
    w1._y2.addItem(c5)

    assert len(w1) == 6
    assert w1[:] == [c0, c1, c2, c3, c4, c5]
    w1_mod_items = w1._cprop_tool.getModifiableItems()
    for c in [c0, c1, c2, c3, c4, c5]:
        assert c0 in w1_mod_items.values()
    assert w1.getViewBox().addedItems == [c0, c2, c4]
    assert w1._y2.addedItems == [c1, c3, c5]

    # test saveConfigFile
    f = tmp_path / "plot.pck"
    with open(str(f), "wb") as ofile:
        w1.saveConfigFile(ofile=ofile)
    assert f.exists()
    assert len(list(tmp_path.iterdir())) == 1

    # test loadConfigFile
    w2 = tpg.TaurusPlot()
    qtbot.addWidget(w2)
    with open(str(f), "rb") as ifile:
        w2.loadConfigFile(ifile=ifile)

    w1_props = w1._cprop_tool._getCurveAppearanceProperties()
    w2_props = w2._cprop_tool._getCurveAppearanceProperties()

    assert len(w1_props) == 6
    assert len(w2_props) == 4
    for k, p_aft in w2_props.items():
        assert k in w1_props
        p_ini = w1_props[k]
        conflicts = p_ini.conflictsWith(p_aft, strict=True)
        msg = "Mismatch in saved/restored curve properties for '{}':".format(k)
        msg += "\n\t Saved:    {}".format(p_ini)
        msg += "\n\t Restored: {}".format(p_aft)
        assert conflicts == [], msg

    # Uncomment for visual checks
    # show_and_wait(qtbot, w1, w2, timeout=3600000)


# def test_save_config_action(qtbot, tmp_path):
#     w1 = tpg.TaurusPlot()
#     qtbot.addWidget(w1)
#
#     w2 = tpg.TaurusPlot()
#     qtbot.addWidget(w2)
#
#     menu = w1.getPlotItem().getViewBox().menu
#     save_action = None
#     for a in menu.actions():
#         # print(a.text())
#         if a.text() == "Save configuration":
#             save_action = a
#             break
#     assert save_action is not None
#     save_action.trigger()
#     # TODO: handle the modal dialog
#     menu = w2.getPlotItem().getViewBox().menu
#     load_action = None
#     for a in menu.actions():
#         # print(a.text())
#         if a.text() == "Retrieve saved configuration":
#             load_action = a
#             break
#     assert load_action is not None
#     load_action.trigger()
#     # TODO: handle the modal dialog
