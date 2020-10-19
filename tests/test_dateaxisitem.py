import taurus_pyqtgraph as tpg
from datetime import datetime
import pytest

try:
    fromisoformat = datetime.fromisoformat
except AttributeError:  # py <3.7

    def fromisoformat(s):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        raise ValueError("cannot convert {}".format(s))


@pytest.mark.parametrize(
    "val_range,expected",
    [
        (
            ["2020-01-01T00:01:00.100", "2020-01-01T00:01:00.500"],
            ["2020-01-01T00:01:00.200", "2020-01-01T00:01:00.400"],
        ),
        (
            ["2020-01-01T00:00:04.900", "2020-01-01T00:00:07.900"],  # d=1s
            [
                "2020-01-01T00:00:05",
                "2020-01-01T00:00:06",
                "2020-01-01T00:00:07",
            ],
        ),
        (
            ["2020-01-01T00:00:04", "2020-01-01T00:00:37"],  # d=10s
            [
                "2020-01-01T00:00:10",
                "2020-01-01T00:00:20",
                "2020-01-01T00:00:30",
            ],
        ),
        (
            ["2020-01-01T00:05:10", "2020-01-01T00:08:50"],  # d=1m
            ["2020-01-01T00:06", "2020-01-01T00:07", "2020-01-01T00:08"],
        ),
        (
            ["2020-01-01T00:45:10", "2020-01-01T01:15:50"],  # d=10m
            ["2020-01-01T00:50", "2020-01-01T01:00", "2020-01-01T01:10"],
        ),
        (
            ["2020-01-01T00:45:10", "2020-01-01T03:15:50"],  # d=1h
            ["2020-01-01T01:00", "2020-01-01T02:00", "2020-01-01T03:00"],
        ),
        (
            ["2020-01-01T00:45:10", "2020-04-01T03:15:50"],  # d=1month
            ["2020-02-01", "2020-03-01", "2020-04-01"],
        ),
        (
            ["2020-01-01T00:45:10", "2023-04-01T03:15:50"],  # d=1y
            ["2021-01-01", "2022-01-01", "2023-01-01"],
        ),
    ],
)
def test_tickValues(qtbot, val_range, expected):
    """
    Check that the tickValues reimplementation returns the expected values
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    a = w.getPlotItem().axes["bottom"]["item"]
    minVal, maxVal = [fromisoformat(v).timestamp() for v in val_range]
    exp = [fromisoformat(v).timestamp() for v in expected]
    assert a.tickValues(minVal, maxVal, 10000)[0][1] == exp


def test_tickValues_overflow(qtbot):
    """
    Check that the tickValues reimplementation returns the expected values
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    a = w.getPlotItem().axes["bottom"]["item"]
    # check that the datetime overflows do not break the call
    assert a.tickValues(-1e19, 0, 1e3) == [(1e19, [])]
    assert a.tickValues(0, 1e19, 1e3) == [(1e19, [])]


@pytest.mark.parametrize(
    "values,expected",
    [
        (
            ["2020-01-01T00:01", "2020-01-01T00:01:00.100"],
            ["[+000000ms]", "[+100000ms]"],
        ),
        (["2020-01-01", "2020-01-01T00:00:05"], ["00:00:00", "00:00:05"],),
        (["2020-01-01", "2020-01-01T00:00:30"], ["00:00:00", "00:00:30"],),
        (["2020-01-01", "2020-01-01T00:05"], ["00:00", "00:05"]),
        (["2020-01-01", "2020-01-01T05:00"], ["Jan/01-00h", "Jan/01-05h"],),
        (["2020-01-01", "2020-01-05"], ["Jan/01", "Jan/05"]),
        (["2020-01-01", "2020-05-01"], ["2020 Jan", "2020 May"]),
        (["2020-01-01", "2023-01-01", "2050-01-01"], ["2020", "2023", "2050"]),
    ],
)
def test_tickStrings(qtbot, values, expected):
    """
    Check that the tickStrings reimplementation returns the expected values
    """
    w = tpg.TaurusTrend()
    qtbot.addWidget(w)
    a = w.getPlotItem().axes["bottom"]["item"]

    dt = [fromisoformat(v).timestamp() for v in values]
    spacing = dt[-1] - dt[0]
    # check return values in the seconds scale
    assert a.tickStrings(dt, None, spacing) == expected
