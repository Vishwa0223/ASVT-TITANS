import plotly.graph_objects as go
import streamlit as st

from src.ui_helpers import ASSET_TICKERS, STRATEGIES, aligned_comparison, apply_theme, chart_layout, render_header, render_sidebar, run_backtest, style_table

st.set_page_config(page_title="QuantX | Backtesting", page_icon="🔬", layout="wide")
apply_theme()
render_sidebar("Backtesting")
render_header("Backtesting", "Evaluate a strategy against historical prices")

asset = st.selectbox("Asset", list(ASSET_TICKERS), key="backtest_asset")
strategy = st.selectbox("Strategy", STRATEGIES, key="backtest_strategy")
initial_capital = st.number_input("Initial capital", min_value=1000.0, value=100000.0, step=1000.0, key="backtest_capital")
transaction_cost = st.number_input("Transaction cost (%)", min_value=0.0, value=0.1, step=0.01, key="backtest_cost")
position_size = st.slider("Position size", min_value=0.05, max_value=1.0, value=1.0, step=0.05, key="backtest_position")

try:
    strategy_data, result, metrics, backtester = run_backtest(asset, strategy, initial_capital, transaction_cost, position_size)
except Exception as exc:
    st.error(f"Backtest execution failed: {exc}")
    st.stop()

st.markdown(f"<div class='section-label'>{strategy} · {asset}</div>", unsafe_allow_html=True)
metric_columns = st.columns(7)
metric_values = [
    ("Strategy return", f"{metrics['Total Return (%)']:.2f}%"),
    ("Buy & hold", f"{metrics['Buy & Hold Return (%)']:.2f}%"),
    ("Sharpe ratio", f"{metrics['Sharpe Ratio']:.2f}"),
    ("Volatility", f"{metrics['Volatility (%)']:.2f}%"),
    ("Max drawdown", f"{metrics['Max Drawdown (%)']:.2f}%"),
    ("Trades", str(backtester.get_num_trades())),
    ("Vs buy & hold", f"{metrics['Strategy vs Buy & Hold (%)']:.2f}%"),
]
for column, (label, value) in zip(metric_columns, metric_values):
    column.metric(label, value)

price_fig = go.Figure(go.Scatter(x=result["Date"], y=result["Close"], name="Price", line={"color": "#8ec5ff", "width": 2.1}))
trade_log = backtester.get_trade_log()
if not trade_log.empty:
    buys = trade_log[trade_log["type"] == "BUY"]
    sells = trade_log[trade_log["type"] == "SELL"]
    if not buys.empty:
        buy_dates = result.loc[buys["index"], "Date"]
        price_fig.add_trace(go.Scatter(x=buy_dates, y=buys["price"], mode="markers", name="BUY", marker={"color": "#4ade80", "symbol": "triangle-up", "size": 10}, customdata=[strategy] * len(buys), hovertemplate="BUY SIGNAL<br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:,.2f}<br>Strategy: %{customdata}<extra></extra>"))
    if not sells.empty:
        sell_dates = result.loc[sells["index"], "Date"]
        price_fig.add_trace(go.Scatter(x=sell_dates, y=sells["price"], mode="markers", name="SELL", marker={"color": "#ff5f7a", "symbol": "triangle-down", "size": 10}, customdata=[strategy] * len(sells), hovertemplate="SELL SIGNAL<br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:,.2f}<br>Strategy: %{customdata}<extra></extra>"))
price_fig.update_layout(title="Executed entries and exits", **chart_layout(360))
st.plotly_chart(price_fig, width="stretch", config={"displayModeBar": False})

fig = go.Figure(go.Scatter(x=result["Date"], y=result["portfolio_value"], name="Strategy equity", line={"color": "#4cc9f0", "width": 2.4}))
fig.update_layout(title="Equity curve", **chart_layout(380))
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

try:
    comparison = aligned_comparison(result, strategy_data, initial_capital)
    comparison_fig = go.Figure()
    comparison_fig.add_trace(go.Scatter(x=comparison["Date"], y=comparison["Strategy"], name="Strategy", line={"color": "#4cc9f0", "width": 2.2}))
    comparison_fig.add_trace(go.Scatter(x=comparison["Date"], y=comparison["Buy & Hold"], name="Buy & hold", line={"color": "#7b61ff", "width": 2.2}))
    comparison_fig.update_layout(title="Strategy vs buy & hold", **chart_layout(350))
    st.plotly_chart(comparison_fig, width="stretch", config={"displayModeBar": False})
except ValueError as exc:
    st.warning(str(exc))

st.subheader("Trade log")
if trade_log.empty:
    st.info("No trades were generated for this configuration.")
else:
    st.dataframe(style_table(trade_log), width="stretch")
