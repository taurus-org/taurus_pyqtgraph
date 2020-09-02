"""
Convenience functions, etc for tests
"""


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


def get_sub_config(cfg, item):
    assert item in cfg["__itemConfigurations__"]
    assert item in cfg["__orderedConfigNames__"]
    return cfg["__itemConfigurations__"][item]
