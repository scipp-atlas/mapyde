from __future__ import annotations

import time

import pytest
from typer.testing import CliRunner

import mapyde
from mapyde.cli import app


@pytest.fixture()
def runner():
    return CliRunner()


def test_version(runner):
    start = time.time()
    result = runner.invoke(app, ["--version"])
    end = time.time()
    elapsed = end - start
    assert result.exit_code == 0
    assert mapyde.__version__ in result.stdout
    # make sure it took less than a second
    assert elapsed < 1.0
