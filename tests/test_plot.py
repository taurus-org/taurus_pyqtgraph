import numpy
import taurus_pyqtgraph as tpg
import pyqtgraph as pg


def _get_sub_config(cfg, item):
    assert item in cfg['__itemConfigurations__']
    assert item in cfg['__orderedConfigNames__']
    return cfg['__itemConfigurations__'][item]


def test_plot_model_setting(qtbot):

    w = tpg.TaurusPlot()
    qtbot.addWidget(w)

    assert len(w) == 0
    assert len(w._model_chooser_tool.getModelNames()) == 0

    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)","eval:2*rand(10)"),
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
    # w.show()
    # def is_closed():
    #     return not w.isVisible()
    # qtbot.wait_until(is_closed, timeout=999999)


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
        ("eval:linspace(-10,20,10)","eval:2*rand(10)"),
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
    assert vb1.addedItems == []
    assert vb2.addedItems == []
    assert w[:] == []
    assert w._model_chooser_tool.getModelNames() == []


    # Uncomment for visual checks
    # w.show()
    # def is_closed():
    #     return not w.isVisible()
    # qtbot.wait_until(is_closed, timeout=999999)

def test_xymodelchooser_config(qtbot):

    w1 = tpg.TaurusPlot()
    qtbot.addWidget(w1)

    models1 = [
        "eval:1*rand(22)",
        ("eval:linspace(-10,20,10)","eval:2*rand(10)"),
    ]

    w1.setModel(models1)

    # test createConfig
    cfg = w1.createConfig()
    xymccfg1 = _get_sub_config(cfg, "XYmodelchooser")
    modelscfg1 = _get_sub_config(xymccfg1, "Models")
    assert modelscfg1[0] == (None, "eval://localhost/@DefaultEvaluator/1*rand(22)" )
    assert modelscfg1[1] == (
        'eval://localhost/@DefaultEvaluator/linspace(-10,20,10)',
        'eval://localhost/@DefaultEvaluator/2*rand(10)'
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
    assert w2._model_chooser_tool.getModelNames() == modelscfg1

    # Uncomment for visual checks
    # w2.show()
    # def is_closed():
    #     return not w.isVisible()
    # qtbot.wait_until(is_closed, timeout=999999)


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
    y2_cfg = _get_sub_config(plot_cfg, "Y2Axis")
    curvescfg1 = _get_sub_config(y2_cfg, "Y2Curves")
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
    # w2.show()
    # def is_closed():
    #     return not w.isVisible()
    # qtbot.wait_until(is_closed, timeout=999999)

