import copy
from taurus.external.qt import Qt
from taurus_pyqtgraph.curveproperties import (
    CurveAppearanceProperties,
    CONFLICT,
)


p_all_conflict = CurveAppearanceProperties()


p1 = CurveAppearanceProperties(
    sStyle="t",
    sSize=2,
    sColor="r",
    sFill=False,
    lStyle=Qt.Qt.DashLine,
    lWidth=3,
    lColor="b",
    cStyle="Lines",
    y2=True,
    cFill=False,
    title="p1, all set",
    visible=True,
)

p2 = CurveAppearanceProperties(
    sStyle=None,
    sSize=-1,
    sColor="b",
    sFill=True,
    lStyle=Qt.Qt.SolidLine,
    lWidth=5,
    lColor="y",
    cStyle="Steps",
    y2=False,
    cFill=True,
    title="p2, all set",
    visible=False,
)

p3 = copy.deepcopy(p1)
p3.sSize = 3
p3.lStyle = CONFLICT

p4 = copy.deepcopy(p1)
p4.sSize = 3
p4.lColor = "g"


def test_curveproperties_conflictsWith(qtbot):
    assert p1.conflictsWith(copy.deepcopy(p1), strict=False) == []
    assert p1.conflictsWith(copy.deepcopy(p1), strict=True) == []
    assert p1.conflictsWith(p_all_conflict, strict=False) == []
    assert p1.conflictsWith(p_all_conflict, strict=True) == p1.propertyList
    assert p1.conflictsWith(p2, strict=False) == p1.propertyList
    assert p1.conflictsWith(p2, strict=True) == p1.propertyList
    assert p1.conflictsWith(p3, strict=False) == ["sSize"]
    assert p1.conflictsWith(p3, strict=True) == ["sSize", "lStyle"]


def test_curveproperties_merge(qtbot):
    merged = p1.merge([p1, p3])
    for a in merged.propertyList:
        if a in ["sSize", "lStyle"]:
            assert getattr(merged, a) == CONFLICT, "mismatch: %s" % a
        else:
            assert getattr(merged, a) == getattr(p1, a), "mismatch: %s" % a

    merged = p1.merge([p1, p3, p4])
    for a in merged.propertyList:
        if a in ["sSize", "lStyle", "lColor"]:
            assert getattr(merged, a) == CONFLICT, "mismatch: %s" % a
        else:
            assert getattr(merged, a) == getattr(p1, a), "mismatch: %s" % a

    merged = p1.merge([p3, p1, p3, p3, p3, p3])
    for a in merged.propertyList:
        if a in ["sSize", "lStyle"]:
            assert getattr(merged, a) == CONFLICT, "mismatch: %s" % a
        else:
            assert getattr(merged, a) == getattr(p1, a), "mismatch: %s" % a

    merged = p1.merge([p1, p3], conflict=p1.inConflict_update_a)
    assert merged.sSize == p3.sSize, "update a with b if they differ"
    assert merged.lStyle == p1.lStyle, "do not update when b is in conflict"
    for a in merged.propertyList:
        if a not in ["sSize", "lStyle"]:
            assert getattr(merged, a) == getattr(p3, a), "mismatch: %s" % a

    merged = p1.merge([p1, p2], conflict=p1.inConflict_update_a)
    for a in merged.propertyList:
        assert getattr(merged, a) == getattr(p2, a), "mismatch: %s" % a

    merged = p1.merge([p1, p_all_conflict], conflict=p1.inConflict_update_a)
    for a in merged.propertyList:
        assert getattr(merged, a) == getattr(p1, a), "mismatch: %s" % a

    merged = p1.merge([p1, p_all_conflict], conflict=p1.inConflict_update_a)
    for a in merged.propertyList:
        assert getattr(merged, a) == getattr(p1, a), "mismatch: %s" % a
