"""Smoke tests (need network: Yahoo Finance). The app must not raise for any interval or
year range, and must show a real Z-score (not NaN) whenever it shows one."""
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


@pytest.mark.parametrize("interval", ["1d", "5d", "1wk", "1mo", "3mo"])
@pytest.mark.parametrize("years", [(2000, 2040), (2022, 2025), (2024, 2025), (2025, 2025), (2039, 2040)])
def test_no_exceptions_and_no_nan_metric(interval, years, monkeypatch):
    at = run(interval, years, monkeypatch)
    assert not at.exception, [e.message for e in at.exception]
    for m in at.metric:
        assert not math.isnan(float(m.value))
    if not at.metric:
        assert at.error   # too little data -> explained, not crashed
