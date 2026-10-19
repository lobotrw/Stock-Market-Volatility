
import datetime

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def main_plot(data):
    # Sample data with datetime index
    df       = pd.DataFrame(data)
    # Create the plot with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=150)

    # Plot Z on the first y-axis
    color="green"
    ax1.set_xlabel('Date', fontsize=5)
    ax1.set_ylabel('Z', color=color, fontsize=5)
    ax1.plot(df.index, df["Z"], color=color, linewidth=0.5)
    ax1.tick_params(axis='y', labelcolor=color, labelsize=5)
    ax1.tick_params(axis='x', labelsize=5)  # Adjust x-axis tick label size
    # Add a dashed horizontal line at Z = 0
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)

    # Shade volatility regimes: Z < -1 calm (green), Z > +1 elevated (red), neutral in between
    lo, hi = min(-4, df["Z"].min()), max(4, df["Z"].max())
    ax1.fill_between(df.index, lo, hi, where=(df["Z"] < -1), color='green', alpha=0.3, linewidth=0,
                     label='VIX calm vs its recent average (Z < -1)')
    ax1.fill_between(df.index, lo, hi, where=(df["Z"] > 1), color='red', alpha=0.3, linewidth=0,
                     label='VIX elevated vs its recent average (Z > +1)')
    ax1.legend(loc='upper left', fontsize=5)

    # Create a second y-axis
    ax2 = ax1.twinx()
    color = "black"
    ax2.set_ylabel('S&P 500 (^GSPC)', color=color, fontsize=5)
    ax2.plot(df.index, df["S&P 500"], color=color, linewidth=1)
    ax2.tick_params(axis='y', labelcolor=color, labelsize=5)

    st.pyplot(fig, width='stretch')


def z_score(src, length):
    """Standard rolling z-score: (x - rolling mean) / rolling population std, both over the
    same trailing ``length`` bars. Causal: a value only uses the current and previous bars."""
    basis = src.rolling(length).mean()
    stdv  = src.rolling(length).std(ddof=0)
    return (src - basis) / stdv


def end_date(end_year, today=None):
    """Exclusive download end that INCLUDES all of ``end_year`` (capped at tomorrow)."""
    today = today or datetime.date.today()
    return min(datetime.date(end_year, 12, 31), today) + datetime.timedelta(days=1)


def forward_return_table(data, horizon=20):
    """Evaluation only (uses future prices by design, never feeds the indicator):
    mean forward S&P 500 return over the next ``horizon`` bars, by Z regime."""
    px   = data["S&P 500"]
    fwd  = px.shift(-horizon) / px - 1
    past = px / px.shift(horizon) - 1
    z    = data["Z"]
    regime = pd.cut(z, [-np.inf, -1, 1, np.inf], labels=["Z < -1 (calm)", "-1 ≤ Z ≤ 1 (neutral)", "Z > +1 (elevated)"])
    df = pd.DataFrame({"regime": regime, "fwd": fwd}).dropna()
    table = df.groupby("regime", observed=False)["fwd"].agg(["mean", "median", "count"])
    table["% positive"] = df.groupby("regime", observed=False)["fwd"].apply(lambda s: (s > 0).mean() * 100)
    table[["mean", "median"]] *= 100
    table.columns = [f"mean fwd {horizon}-bar return %", "median %", "n bars", "% positive"]
    ok = z.notna() & fwd.notna()
    corr_fwd  = float(np.corrcoef(z[ok], fwd[ok])[0, 1]) if ok.sum() > 2 else float("nan")
    okp = z.notna() & past.notna()
    corr_past = float(np.corrcoef(z[okp], past[okp])[0, 1]) if okp.sum() > 2 else float("nan")
    return table, corr_fwd, corr_past
