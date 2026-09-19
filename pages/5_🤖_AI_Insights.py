import streamlit as st

from src.ai_analysis import analyze_market
from src.ui_helpers import ASSET_TICKERS, STRATEGIES, apply_strategy, apply_theme, load_asset_data, render_header, render_sidebar, run_backtest

st.set_page_config(page_title="QuantX | AI Insights", page_icon="🤖", layout="wide")
apply_theme()
render_sidebar("AI insights")
render_header("AI insights", "AI-generated interpretation grounded in selected market data")

asset = st.selectbox("Asset", list(ASSET_TICKERS), key="ai_asset")
strategy = st.selectbox("Strategy context", STRATEGIES, key="ai_strategy")
data = load_asset_data(asset)
strategy_data = apply_strategy(data, strategy)

try:
    _, _, metrics, backtester = run_backtest(asset, strategy, 100000.0, 0.1, 1.0)
except Exception as exc:
    st.error(f"The analysis inputs could not be prepared: {exc}")
    st.stop()

latest = strategy_data.iloc[-1]
signal = {1: "BUY", -1: "SELL", 0: "HOLD"}[int(latest["Signal"])]
prompt = f"""You are a quantitative finance research assistant. Analyze historical data for {asset} ({ASSET_TICKERS[asset]}), using {strategy} as the strategy context. Current signal: {signal}. Latest close: {latest['Close']:.4f}. Daily return: {latest['Daily_Return'] * 100:.2f}%. Cumulative return: {latest['Cumulative_Return'] * 100:.2f}%. Annualized volatility: {latest['Annualized_Volatility'] * 100:.2f}%. Backtest total return: {metrics['Total Return (%)']:.2f}%. Sharpe ratio: {metrics['Sharpe Ratio']:.2f}. Maximum drawdown: {metrics['Max Drawdown (%)']:.2f}%. Number of trades: {backtester.get_num_trades()}. Provide four concise labeled sections: Market Summary, Trend Analysis, Risk Observations, Strategy Observations. Discuss historical evidence only and do not make guaranteed predictions."""

st.markdown(f"<div class='section-label'>{asset} · {strategy} · current signal: {signal}</div>", unsafe_allow_html=True)
try:
    response = analyze_market(prompt)
    if not response or not response.strip():
        raise RuntimeError("The AI service returned an empty response.")
    st.markdown(response)
except Exception:
    st.error("AI insights are unavailable right now. Configure FEATHERLESS_API_KEY in the environment and try again. No API key is displayed or stored by this page.")
    st.info("The selected market data and strategy context are ready, but the external AI service did not return an analysis.")

with st.expander("Analysis inputs"):
    st.json({
        "asset": asset,
        "ticker": ASSET_TICKERS[asset],
        "strategy": strategy,
        "latest_signal": signal,
        "annualized_volatility_percent": round(float(latest["Annualized_Volatility"] * 100), 2),
        "backtest_metrics": metrics,
    })
