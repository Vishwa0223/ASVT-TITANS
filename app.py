import streamlit as st
import pandas as pd

from src.data_loader import load_data
from src.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_returns,
    calculate_volatility,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ASVT TITANS",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("ASVT TITANS")
st.subheader("Multi-Asset Quantitative Trading & Risk Analytics")

# --------------------------------------------------
# ASSET TICKERS
# --------------------------------------------------

asset_tickers = {
    "Gold": "GC=F",
    "Bitcoin": "BTC-USD",
    "NVIDIA": "NVDA"
}

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Dashboard Settings")

asset = st.sidebar.selectbox(
    "Select Asset",
    ["Gold", "Bitcoin", "NVIDIA"]
)

strategy = st.sidebar.selectbox(
    "Select Strategy",
    [
        "SMA Crossover",
        "EMA Trend",
        "Momentum",
        "Mean Reversion"
    ]
)

initial_capital = st.sidebar.number_input(
    "Initial Capital",
    min_value=1000.0,
    value=100000.0,
    step=1000.0
)

transaction_cost = st.sidebar.number_input(
    "Transaction Cost (%)",
    min_value=0.0,
    value=0.1,
    step=0.01
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

ticker = asset_tickers[asset]

st.info(f"Loading historical data for {asset}...")

try:
    data = load_data(ticker)

    # Calculate indicators
    data = calculate_sma(data, period=20)
    data = calculate_ema(data, period=20)
    data = calculate_returns(data)
    data = calculate_volatility(data, period=20)

except Exception as e:
    st.error(f"Unable to load market data: {e}")
    st.stop()

# --------------------------------------------------
# CURRENT SELECTION
# --------------------------------------------------

st.write("### Current Selection")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Asset", asset)

with col2:
    st.metric("Strategy", strategy)

with col3:
    st.metric(
        "Initial Capital",
        f"${initial_capital:,.2f}"
    )

with col4:
    st.metric(
        "Transaction Cost",
        f"{transaction_cost}%"
    )

# --------------------------------------------------
# PRICE INFORMATION
# --------------------------------------------------

st.write("### Market Data")

latest_price = float(data["Close"].iloc[-1])

previous_price = float(data["Close"].iloc[-2])

price_change = latest_price - previous_price

price_change_percent = (
    price_change / previous_price
) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Price",
        f"${latest_price:,.2f}"
    )

with col2:
    st.metric(
        "Daily Change",
        f"${price_change:,.2f}"
    )

with col3:
    st.metric(
        "Daily Change %",
        f"{price_change_percent:.2f}%"
    )

# --------------------------------------------------
# PRICE CHART
# --------------------------------------------------

st.write("### Price & Moving Averages")

chart_data = data[
    ["Close", "SMA", "EMA"]
].dropna()

st.line_chart(chart_data)

# --------------------------------------------------
# RETURNS
# --------------------------------------------------

st.write("### Returns")

returns_col1, returns_col2 = st.columns(2)

with returns_col1:
    cumulative_return = (
        float(data["Cumulative_Return"].iloc[-1])
        * 100
    )

    st.metric(
        "Cumulative Return",
        f"{cumulative_return:.2f}%"
    )

with returns_col2:
    daily_return = (
        float(data["Daily_Return"].iloc[-1])
        * 100
    )

    st.metric(
        "Latest Daily Return",
        f"{daily_return:.2f}%"
    )

# --------------------------------------------------
# VOLATILITY
# --------------------------------------------------

st.write("### Volatility")

vol_col1, vol_col2 = st.columns(2)

with vol_col1:
    volatility = float(
        data["Volatility"].iloc[-1]
    ) * 100

    st.metric(
        "20-Day Volatility",
        f"{volatility:.2f}%"
    )

with vol_col2:
    annualized_volatility = float(
        data["Annualized_Volatility"].iloc[-1]
    ) * 100

    st.metric(
        "Annualized Volatility",
        f"{annualized_volatility:.2f}%"
    )

# --------------------------------------------------
# RECENT DATA
# --------------------------------------------------

st.write("### Recent Market Data")

display_columns = [
    "Close",
    "SMA",
    "EMA",
    "Daily_Return",
    "Cumulative_Return",
    "Volatility",
    "Annualized_Volatility"
]

st.dataframe(
    data[display_columns].tail(10),
    use_container_width=True
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.info(
    "Historical market data is used for quantitative analysis. "
    "Past performance does not guarantee future returns."
)