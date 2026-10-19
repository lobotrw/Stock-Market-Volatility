"""Offline unit tests for functions.py."""
import datetime as dt
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from functions import end_date, forward_return_table, z_score  # noqa: E402


def series(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return pd.Series(20 + np.cumsum(rng.normal(0, 1, n)), index=pd.bdate_range("2020-01-01", periods=n))


def test_z_score_is_standard_rolling_z():
    s = series()
    z = z_score(s, 40)
    w = s.iloc[-40:]
    assert z.iloc[-1] == pytest.approx((w.iloc[-1] - w.mean()) / w.std(ddof=0))
    assert z.iloc[:39].isna().all() and not np.isnan(z.iloc[39])   # warm-up = length - 1 bars


def test_z_score_has_no_lookahead():
    s = series(300)
    early = z_score(s.iloc[:200], 40)
    full = z_score(s, 40)
    pd.testing.assert_series_equal(early, full.iloc[:200])


def test_end_date_includes_whole_end_year_and_caps_at_today():
    assert end_date(2024, today=dt.date(2026, 10, 19)) == dt.date(2025, 1, 1)
    assert end_date(2026, today=dt.date(2026, 10, 19)) == dt.date(2026, 10, 20)


def test_forward_return_table_buckets_and_correlations():
    idx = pd.bdate_range("2020-01-01", periods=6)
    data = pd.DataFrame({"S&P 500": [100, 110, 121, 121, 110, 100.0],
                         "Z": [-2.0, 0.0, 2.0, -2.0, 0.0, 2.0]}, index=idx)
    table, corr_fwd, corr_past = forward_return_table(data, horizon=1)
    calm = table.loc["Z < -1 (calm)"]
    # calm days: day0 -> +10 %, day3 -> 110/121-1 = -9.09 %
    assert calm.iloc[0] == pytest.approx((10 + (110 / 121 - 1) * 100) / 2)
    assert calm["n bars"] == 2
    assert -1 <= corr_fwd <= 1 and -1 <= corr_past <= 1
