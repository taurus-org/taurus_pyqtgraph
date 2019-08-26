#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `taurus_pyqtgraph` package."""


from click.testing import CliRunner


def test_smoke():
    import taurus_pyqtgraph  # noqa


def test_command_line_interface():
    """Test the CLI."""
    from taurus_pyqtgraph import cli

    runner = CliRunner()
    result = runner.invoke(cli.tpg)
    assert result.exit_code == 0
    assert "Taurus-pyqtgraph related commands" in result.output
    help_result = runner.invoke(cli.tpg, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output
