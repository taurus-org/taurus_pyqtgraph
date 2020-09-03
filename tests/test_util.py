import taurus_pyqtgraph as tpg
import pytest


class _DummyPlotItem:
    def __init__(self, names):
        self.ditems = [_DummyDataItem(n) for n in names]

    def listDataItems(self):
        return self.ditems[:]


class _DummyDataItem:
    def __init__(self, name):
        self.opts = {"name": name}

    def name(self):
        return self.opts["name"]


@pytest.mark.parametrize(
    "name,existing,expected",
    [
        ("a", list("qwerty"), "a"),
        ("a", list("asdfgh"), "a (2)"),
        ("a", ["a", "a (2)", "a (3)", "b"], "a (4)"),
    ],
)
def test_unique_data_item_name(name, existing, expected):
    assert tpg.unique_data_item_name(name, existing) == expected


@pytest.mark.parametrize(
    "name,existing,expected",
    [
        ("a", list("qwerty"), "a"),
        ("a", list("asdfgh"), "a (2)"),
        ("a", ["a", "a (2)", "a (3)", "b"], "a (4)"),
    ],
)
def test_ensure_unique_curve_name(name, existing, expected):
    plotItem = _DummyPlotItem(existing)
    dataItem = _DummyDataItem(name)
    out = tpg.ensure_unique_curve_name(dataItem, plotItem)
    assert out.name() == expected
