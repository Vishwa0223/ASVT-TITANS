import plotly.graph_objects as go
import streamlit as st

from src.ui_helpers import ASSET_TICKERS, STRATEGIES, add_price_trace, add_signal_traces, apply_strategy, apply_theme, chart_layout, load_asset_data, render_header, render_sidebar, signal_label, signal_points, signal_summary

st.set_page_config(page_title="QuantX | Strategies", page_icon="🧠", layout="wide")
apply_theme()
render_sidebar("Strategies")
render_header("Strategies", "Real strategy signals from the existing engine")

asset = st.selectbox("Asset", list(ASSET_TICKERS), key="strategies_asset")
strategy_name = st.selectbox("Strategy", STRATEGIES, key="strategies_strategy")
data = apply_strategy(load_asset_data(asset), strategy_name)
buys, sells = signal_points(data)
summary_data = signal_summary(data)

st.markdown(f"<div class='section-label'>{strategy_name} · {asset}</div>", unsafe_allow_html=True)
summary = st.columns(4)
summary[0].metric("Rows analyzed", f"{len(data):,}")
summary[1].metric("Buy signals", f"{len(buys):,}")
summary[2].metric("Sell signals", f"{len(sells):,}")
summary[3].metric("Latest signal", summary_data["latest"])

signal_cards = st.columns(4)
signal_cards[0].metric("🟢 BUY signals", summary_data["buy_count"])
signal_cards[1].metric("🔴 SELL signals", summary_data["sell_count"])
signal_cards[2].metric("⚪ HOLD / no signal", summary_data["hold_count"])
signal_cards[3].metric("Last signal", summary_data["latest"])

fig = go.Figure()
add_price_trace(fig, data)
indicator = {"SMA Crossover": ["SMA_Short", "SMA_Long"], "EMA Trend": ["EMA"], "Momentum": [], "Mean Reversion": ["Mean"]}[strategy_name]
colors = ["#7b61ff", "#4cc9f0"]
for column, color in zip(indicator, colors):
    fig.add_trace(go.Scatter(x=data.index, y=data[column], name=column.replace("_", " "), line={"color": color, "width": 1.8}))
add_signal_traces(fig, data, strategy_name)
fig.update_layout(**chart_layout(480))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.subheader("Strategy output")
output_columns = [column for column in ["Close", "SMA_Short", "SMA_Long", "EMA", "Momentum", "Mean", "Deviation", "Signal"] if column in data]
st.dataframe(data[output_columns].tail(30), width="stretch")

st.subheader("Signal table")
changes = data["Signal"].diff().fillna(data["Signal"])
events = data[(data["Signal"].isin([1, -1])) & (changes != 0)].copy()
events["Date"] = events.index.strftime("%Y-%m-%d")
events["Price"] = events["Close"].round(2)
events["Signal"] = events["Signal"].map(signal_label)
st.dataframe(events[["Date", "Price", "Signal"]].tail(40), width="stretch", hide_index=True)
