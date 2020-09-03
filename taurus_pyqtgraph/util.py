def unique_data_item_name(name, existing):
    """Accepts a name and a list of existing names and
    returns a name qhich may be modified with a numerical
    suffix such as " (1)", or " (2)", etc in order to avoid
    duplications with the existing names
    """
    base = name
    i = 1
    while name in existing:
        i += 1
        name = "{} ({})".format(base, i)
    return name


def ensure_unique_curve_name(dataItem, plotItem):
    """Given a plotItem, it changes its name adding a prefix as in
    `unique_data_item_name`" to avoid duplication of names with respect
    to the plotDataItems contained in Sardana
    """
    name = dataItem.name()
    if name is None:
        return dataItem
    existing = [e.name() for e in plotItem.listDataItems()]
    new_name = unique_data_item_name(name, existing)
    if new_name != name:
        dataItem.opts["name"] = new_name
    return dataItem
