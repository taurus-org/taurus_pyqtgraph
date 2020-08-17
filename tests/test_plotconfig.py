import taurus_pyqtgraph as tpg


def _get_sub_config(cfg, item):
    assert item in cfg['__itemConfigurations__']
    assert item in cfg['__orderedConfigNames__']
    return cfg['__itemConfigurations__'][item]


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

    # Debugging
    # from pprint import pprint
    # pprint(cfg)
    # pprint(modelscfg1)

    # test applyConfig
    w2 = tpg.TaurusPlot()
    qtbot.addWidget(w2)
    assert len(w2._model_chooser_tool.getModelNames()) == 0

    w2.applyConfig(cfg)
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
        ("eval:linspace(-10,20,10)","eval:2*rand(10)"),
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
