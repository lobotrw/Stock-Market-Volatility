### Stock Market Volatility Regime

**Purpose:**
Shows the VIX (CBOE Volatility Index) as a rolling Z-score against its own recent average, next to the S&P 500 index (^GSPC). It describes the **current volatility regime**: whether the VIX is calm or elevated compared with recent weeks. It is **not** a forecast of S&P 500 direction (see *What the data shows*).
![plot](components/main.png)

**Key Concepts:**

1. **Z-Score:** `(VIX − rolling mean) / rolling std` over the last *Z Score Length* bars, using only current and past bars.

2. **Shading:**
   - **Z < −1 (green):** VIX is well below its recent average, so the market is calm.
   - **Z > +1 (red):** VIX is well above its recent average, so volatility is elevated. This usually follows a decline that has already happened.
   - Between −1 and +1 there is no shading (neutral).

3. **Settings:**
   - **TimeFrame:** 1 day, 5 days, 1 week, 1 month, 3 months.
   - **Start & End Years:** both years are included in full, and the end year runs up to today.
   - **Z Score Length:** the rolling window, in bars.
![plot](components/settings.png)

**What the data shows** (^GSPC and ^VIX daily, 2000-01-03 to 2026-10-16, Z length 40):
- Mean forward S&P 500 return after days with the old "red" (Z > 0) shading was *higher* than after "green" (Z ≤ 0) days: 20 days ahead, +0.83 % vs +0.47 %.
- The Z-score correlates with the **past** 20-day return (−0.60), but hardly at all with the **next** 20-day return (+0.03).
- So the indicator describes what already happened; it does not predict a trend. The app shows a forward-return-by-regime table for whatever period you select, so you can check this yourself.

*This app is not financial advice.*
