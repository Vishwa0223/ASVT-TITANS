import plotly.graph_objects as go
import streamlit as st
from itertools import combinations

from src.indicators import calculate_correlation, calculate_rolling_correlation
from src.metrics import max_drawdown, sharpe_ratio
from src.ui_helpers import ASSET_TICKERS, apply_theme, chart_layout, load_asset_data, render_header, render_sidebar

st.set_page_config(page_title="QuantX | Risk Analysis", page_icon="⚠️", layout="wide")
apply_theme()
render_sidebar("Risk analysis")
render_header("Risk analysis", "Portfolio risk and cross-asset relationships")

selected_assets = st.multiselect("Assets", list(ASSET_TICKERS), default=list(ASSET_TICKERS), key="risk_assets")
if len(selected_assets) < 2:
    st.info("Select at least two assets to calculate correlations.")
    st.stop()

asset_data = {asset: load_asset_data(asset) for asset in selected_assets}
prices = __import__("pandas").DataFrame({asset: data["Close"] for asset, data in asset_data.items()}).dropna()
returns = prices.pct_change().dropna()

st.markdown("<div class='section-label'>Risk snapshot</div>", unsafe_allow_html=True)
columns = st.columns(len(selected_assets))
for column, asset in zip(columns, selected_assets):
    equity = (1 + returns[asset]).cumprod()
    column.metric(f"{asset} volatility", f"{returns[asset].std() * (252 ** 0.5) * 100:.2f}%")
    column.metric(f"{asset} max drawdown", f"{max_drawdown(equity):.2f}%")
    column.metric(f"{asset} Sharpe", f"{sharpe_ratio(equity):.2f}")

correlation = calculate_correlation(prices)
heatmap = go.Figure(go.Heatmap(z=correlation.values, x=correlation.columns, y=correlation.index, zmin=-1, zmax=1, zmid=0, colorscale="RdBu_r", colorbar={"title": "Correlation"}))
heatmap.update_layout(title="Return correlation matrix", **chart_layout(400))
st.plotly_chart(heatmap, width="stretch", config={"displayModeBar": False})

pairs = list(combinations(selected_assets, 2))
pair_labels = [f"{first} / {second}" for first, second in pairs]
pair_label = st.selectbox("Rolling correlation pair", pair_labels, key="risk_pair")
first, second = pairs[pair_labels.index(pair_label)]
rolling = calculate_rolling_correlation(prices[[first, second]], window=30)
rolling_series = rolling.xs(second, level=1)[first].dropna()
rolling_fig = go.Figure(go.Scatter(x=rolling_series.index, y=rolling_series, name="30-day rolling correlation", line={"color": "#4cc9f0", "width": 2.1}))
rolling_fig.add_hline(y=0, line_dash="dot", line_color="rgba(73,49,41,.3)")
rolling_fig.update_layout(title=f"30-day rolling correlation · {first} / {second}", **chart_layout(320))
st.plotly_chart(rolling_fig, width="stretch", config={"displayModeBar": False})
