import streamlit as st

st.set_page_config(
    page_title="ASVT TITANS",
    layout="wide"
)

st.title("ASVT TITANS")
st.subheader("Multi-Asset Quantitative Trading & Risk Analytics")

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
    value=100000.0
)

transaction_cost = st.sidebar.number_input(
    "Transaction Cost (%)",
    min_value=0.0,
    value=0.1
)

st.write("### Current Selection")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Asset", asset)

with col2:
    st.metric("Strategy", strategy)

with col3:
    st.metric("Initial Capital", f"${initial_capital:,.2f}")

with col4:
    st.metric("Transaction Cost", f"{transaction_cost}%")

st.info("Dashboard components will be connected to the team's data, strategy, and backtesting modules.")