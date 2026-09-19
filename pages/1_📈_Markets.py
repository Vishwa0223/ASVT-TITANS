import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ui_helpers import (
    ASSET_TICKERS,
    STRATEGIES,
    add_signal_traces,
    apply_strategy,
    apply_theme,
    chart_layout,
    load_asset_data,
    render_header,
    render_sidebar,
    signal_label,
    signal_summary,
)

st.set_page_config(page_title="QuantX | Markets", page_icon="📈", layout="wide")
apply_theme()
render_sidebar("Markets")
render_header("Markets", "Real historical prices, indicators, and strategy signals")

asset = st.selectbox("Asset", list(ASSET_TICKERS), key="markets_asset")
strategy = st.selectbox("Signal strategy", STRATEGIES, key="markets_strategy")
strategy_data = apply_strategy(load_asset_data(asset), strategy)
latest = strategy_data.iloc[-1]
summary = signal_summary(strategy_data)

st.markdown(f"<div class='section-label'>{asset} · {ASSET_TICKERS[asset]} · {strategy}</div>", unsafe_allow_html=True)
metrics = st.columns(6)
metrics[0].metric("Latest price", f"${latest['Close']:,.2f}")
metrics[1].metric("Daily return", f"{latest['Daily_Return'] * 100:.2f}%")
metrics[2].metric("SMA", f"${latest['SMA']:,.2f}")
metrics[3].metric("EMA", f"${latest['EMA']:,.2f}")
metrics[4].metric("Volatility", f"{latest['Volatility'] * 100:.2f}%")
metrics[5].metric("Annualized volatility", f"{latest['Annualized_Volatility'] * 100:.2f}%")

signal_columns = st.columns(4)
signal_columns[0].metric("Current signal", signal_label(int(latest["Signal"])))
signal_columns[1].metric("BUY signals", summary["buy_count"])
signal_columns[2].metric("SELL signals", summary["sell_count"])
signal_columns[3].metric("HOLD / no signal", summary["hold_count"])

last_buy = pd.Timestamp(summary["last_buy"]).strftime("%Y-%m-%d") if summary["last_buy"] is not None else "None"
last_sell = pd.Timestamp(summary["last_sell"]).strftime("%Y-%m-%d") if summary["last_sell"] is not None else "None"
st.markdown(
    f"<div class='glass-panel'><div class='section-label'>Current signal</div><div style='font-size:1.8rem;font-weight:800;color:{'#69e49b' if summary['latest'] == 'BUY' else '#ff7b9b' if summary['latest'] == 'SELL' else '#c4d0e4'};'>{'🟢' if summary['latest'] == 'BUY' else '🔴' if summary['latest'] == 'SELL' else '⚪'} {summary['latest']}</div><div class='muted' style='margin-top:.5rem;'>Last BUY signal: {last_buy} · Last SELL signal: {last_sell}</div></div>",
    unsafe_allow_html=True,
)

fig = go.Figure()
fig.add_trace(go.Scatter(x=strategy_data.index, y=strategy_data["Close"], name="Price", line={"color": "#8ec5ff", "width": 2.4}))
fig.add_trace(go.Scatter(x=strategy_data.index, y=strategy_data["SMA"], name="SMA (20)", line={"color": "#7b61ff", "width": 1.8}))
fig.add_trace(go.Scatter(x=strategy_data.index, y=strategy_data["EMA"], name="EMA (20)", line={"color": "#4cc9f0", "width": 1.8}))
add_signal_traces(fig, strategy_data, strategy)
fig.update_layout(**chart_layout(500))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.subheader("Signal history")
buys, sells = [], []
changes = strategy_data["Signal"].diff().fillna(strategy_data["Signal"])
events = strategy_data[(strategy_data["Signal"].isin([1, -1])) & (changes != 0)].copy()
events["Date"] = events.index.strftime("%Y-%m-%d")
events["Price"] = events["Close"].round(2)
events["Signal"] = events["Signal"].map(signal_label)
st.dataframe(events[["Date", "Price", "Signal"]].tail(30), width="stretch", hide_index=True)
