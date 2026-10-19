# Import necessary libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import numpy as np
from   functions import main_plot, z_score, end_date, forward_return_table
import matplotlib.pyplot as plt

# Set up the Streamlit app configuration
st.set_page_config(
    page_title              = "Stock Market Volatility",
    page_icon               = "🔃",
    layout                  = "wide",
    initial_sidebar_state   = "collapsed"
)

# CSS to hide Streamlit menu, footer, and header for cleaner UI
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# CSS to hide Streamlit sidebar and collapse control button
st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                visibility: hidden
            }

            [data-testid="collapsedControl"] {
                visibility: hidden
            }
            </style>
            """, unsafe_allow_html=True)

# Load HTML components for navigation and description
navbar         = open('components/navbar.txt').read()
vix_           = open('components/vix.txt').read()
desc           = open('components/description.txt').read()
navbar_bottom  = open('components/navbar_bottom.txt').read()

# Render top navigation bar
st.markdown(navbar, unsafe_allow_html=True)

# Define a function to download S&P 500 data and cache it for optimized performance
@st.cache_data(ttl=3600, show_spinner=False)
def download_data(ticker, start, end, interval):
    data = yf.download(ticker, 
                       start    = start, 
                       end      = end,
                       interval = interval,
                       auto_adjust       = False,   # keep the "Adj Close" column
                       multi_level_index = False,   # flat columns (yfinance >= 0.2.48)
                       progress          = False)
    return data

# Layout setup using Streamlit columns
col1, col2, col3, _ = st.columns([0.8, 10, 3, 0.4])

# Settings section for user inputs
with col3:
    st.write("#")
    st.subheader("Settings")
    
    # Selectbox for timeframe interval
    interval = st.selectbox("TimeFrame", ('1d', '5d', '1wk', '1mo', '3mo'))
    
    # Slider to select start and end years
    this_year = datetime.date.today().year
    year = st.slider("**Select Start & End Years:**", 2000, this_year, (this_year - 3, this_year),
                     help="Both years are included in full; the end year runs up to today.")
    
    # Divider line
    st.write("---")
    
    # Number input for Z Score Length
    z_len = st.number_input("Z Score Length", 2, 100, 40, step=1)
    
    # Convert selected years to datetime format for data fetching
    start_year = datetime.datetime(year[0], 1, 1)
    end_year   = end_date(year[1])          # exclusive end -> includes all of year[1]

    # Fetch data for S&P 500 (^GSPC) and VIX (^VIX)
    spy = download_data("^GSPC", start_year, end=end_year, interval=interval)
    vix = download_data("^VIX", start_year, end=end_year, interval=interval)

    # Prepare DataFrame for data processing
    data = pd.DataFrame()
    data["S&P 500"] = spy["Adj Close"]
    data["VIX"] = vix["Close"]

    # S&P 500 and VIX are downloaded separately; keep only bars present in both, otherwise the
    # rolling Z-score of VIX turns NaN wherever the two calendars (e.g. 5d bars) disagree
    data = data.dropna()

    if data.shape[0] < z_len + 1:   # first Z needs z_len bars, the delta needs one more
        st.error(f"Not enough data for {year[0]}-{year[1]} at interval {interval} "
                 f"({data.shape[0]} bars) for a Z-score length of {z_len}. "
                 "Widen the year range or use a shorter interval.")
        st.stop()

    # Calculate Z-score based on VIX data and user-defined length
    data["Z"] = z_score(data["VIX"], z_len)

    # Calculate latest Z-score and delta from previous value
    z_sc  = np.round(data["Z"].iloc[-1], 2)
    delta = np.round(data["Z"].iloc[-1] - data["Z"].iloc[-2], 2)

    # Display Z-score metrics
    st.write("#")
    st.write("#")
    c1, c2, c3 = st.columns([1.5, 1, 1])
    c2.metric(label=f"Z-Score VIX (as of {data.index[-1]:%Y-%m-%d})", value=z_sc, delta=delta,
              delta_color="inverse")   # rising volatility shown red

    # Display main content in col2
    with col2:
        # Subheader for Z-score of VIX and the S&P 500
        st.subheader("Z-score of VIX and the S&P 500")

        # Display main plot with data
        main_plot(data)
        
        # Display description text below main plot
        st.write(desc)

        # Honest check of the "does it predict?" question on the selected data
        horizon = 20
        table, corr_fwd, corr_past = forward_return_table(data, horizon)
        st.markdown(f"**Does the Z-score predict the S&P 500?** Forward returns over the next {horizon} bars by "
                    f"VIX regime, {data.index[0]:%Y-%m-%d} – {data.index[-1]:%Y-%m-%d}. This table uses future prices "
                    "on purpose to evaluate the indicator; the indicator itself uses only past bars.")
        st.dataframe(table.round(2), width="stretch")
        st.caption(f"corr(Z, next {horizon}-bar return) = {corr_fwd:+.2f} · corr(Z, previous {horizon}-bar return) = "
                   f"{corr_past:+.2f}. A Z that correlates with the past but not the future describes what already "
                   "happened; it is not a forecast. Overlapping windows: treat the numbers as descriptive.")

        # Divider and additional content
        st.markdown("***")
        st.subheader("CBOE Volatility Index")
        
        # Display line chart for VIX
        st.line_chart(data, y="VIX", color="#d1a626", height=300, width="stretch")
        
        # Additional text content
        st.markdown(vix_)

# Render bottom navigation bar
st.write("---")

with st.expander("**About**"):
    st.write('''
        ### Stock Market Volatility Regime Overview

        **Purpose:**
        Shows how the VIX (CBOE Volatility Index) compares with its own recent average, as a rolling Z-score,
        next to the S&P 500 index (^GSPC). It describes the **current volatility regime**. It is not a
        trading signal or a forecast.

        **Key Concepts:**

        1. **Z-Score Definition:** (VIX − rolling mean) / rolling standard deviation over the last *Z Score Length* bars.
           Only current and past bars are used.

        2. **Interpreting the shading:**
        - **Z < −1 (green):** VIX is well below its recent average, so the market is calm compared with recent weeks.
        - **Z > +1 (red):** VIX is well above its recent average, so volatility is elevated. This usually happens
          *after* the S&P 500 has already fallen.

        3. **What the data shows:** On S&P 500 history since 2000, forward returns after high-Z days were **not**
           lower than after low-Z days (they were slightly higher), and the Z-score correlates strongly with
           *past* returns but hardly with *future* ones. See the table under the chart for the period you selected.
            ''')

st.markdown("""
    Stock Volatility Web Application is not financial advice.
    
    \nAuthor @VanHe1sing\n X: https://x.com/Van_He1sing\n TradingView: https://www.tradingview.com/u/VanHe1sing/\n Telegram: https://t.me/IvanKocherzhat
    """)

# Render bottom navigation bar content
st.markdown(navbar_bottom, unsafe_allow_html=True)
