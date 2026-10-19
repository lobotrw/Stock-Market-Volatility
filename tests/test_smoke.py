"""Smoke tests (need network: Yahoo Finance). The app must not raise for any interval or
year range, and must show a real Z-score (not NaN) whenever it shows one."""
import datetime
import math
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def run(interval, years, monkeypatch):
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "main.py"), default_timeout=300)
    at.run()
    at.selectbox[0].set_value(interval)
    at.slider[0].set_value(years)
    at.run()
    return at


Y = datetime.date.today().year


@pytest.mark.parametrize("interval", ["1d", "5d", "1wk", "1mo", "3mo"])
@pytest.mark.parametrize("years", [(2000, Y), (Y - 3, Y), (Y - 1, Y), (Y, Y), (2024, 2025)])
def test_no_exceptions_and_no_nan_metric(interval, years, monkeypatch):
    at = run(interval, years, monkeypatch)
    assert not at.exception, [e.message for e in at.exception]
    for m in at.metric:
        assert not math.isnan(float(m.value))
    if not at.metric:
        assert at.error   # too little data -> explained, not crashed


def test_default_view_reaches_today(monkeypatch):
    """The default end year must include the latest bars (it used to stop at Dec 31 of the previous year)."""
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "main.py"), default_timeout=300)
    at.run()
    assert not at.exception
    label = at.metric[0].label
    as_of = datetime.date.fromisoformat(label.split("as of ")[1].rstrip(")"))
    assert (datetime.date.today() - as_of).days <= 7
    assert at.dataframe, "forward-return evaluation table is shown"
