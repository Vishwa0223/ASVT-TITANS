from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.backtest import Backtester
from src.data_loader import load_data
from src.indicators import (
    calculate_ema,
    calculate_returns,
    calculate_sma,
    calculate_volatility,
)
from src.strategies import (
    ema_trend_strategy,
    mean_reversion_strategy,
    momentum_strategy,
    sma_crossover_strategy,
)

ASSET_TICKERS = {
    "Gold": "GC=F",
    "Bitcoin": "BTC-USD",
    "NVIDIA": "NVDA",
}

STRATEGIES = ["SMA Crossover", "EMA Trend", "Momentum", "Mean Reversion"]


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --text:#edf6ff; --muted:#a8bddf; --border:rgba(148,163,184,.15); }
        html, body, [data-testid="stAppViewContainer"] {
            background:linear-gradient(180deg,#050d1d 0%,#0b1630 42%,#0b1021 100%);
            color:var(--text);
        }
        .block-container { max-width:1500px; padding-top:1.3rem; padding-bottom:3rem; }
        .topbar, .glass-panel {
            background:linear-gradient(180deg,rgba(14,25,44,.92),rgba(10,17,29,.84));
            border:1px solid var(--border); border-radius:1rem;
            box-shadow:0 18px 42px rgba(2,8,23,.36);
        }
        .topbar { padding:.8rem 1rem; margin-bottom:1.2rem; }
        .glass-panel { padding:1rem; }
        .brand-wrap { display:flex; align-items:center; gap:.7rem; }
        .brand-mark { width:2.2rem; height:2.2rem; display:flex; align-items:center; justify-content:center;
            border-radius:.75rem; background:linear-gradient(135deg,rgba(76,201,240,.35),rgba(123,97,255,.55));
            border:1px solid rgba(255,255,255,.14); font-weight:800; }
        .brand-title { font-weight:800; letter-spacing:.04em; }
        .brand-sub, .muted { color:var(--muted); }
        .brand-sub { font-size:.68rem; letter-spacing:.08em; text-transform:uppercase; }
        .section-label { color:var(--muted); font-size:.7rem; letter-spacing:.13em; text-transform:uppercase;
            font-weight:700; margin-bottom:.65rem; }
        .stButton > button { border-radius:.75rem; border:1px solid rgba(148,163,184,.2);
            background:linear-gradient(135deg,rgba(58,134,255,.2),rgba(123,97,255,.2)); color:var(--text); font-weight:700; }
        .stMetric { background:rgba(10,18,35,.6); border:1px solid var(--border); border-radius:.9rem; padding:.65rem; }
        .stDataFrame { border-radius:.9rem; overflow:hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="topbar"><div class="brand-wrap"><div class="brand-mark">Q</div><div>
        <div class="brand-title">QuantX · {title}</div><div class="brand-sub">{subtitle}</div>
        </div></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active_page: str) -> None:
    with st.sidebar:
        st.markdown("<div class='brand-wrap'><div class='brand-mark'>Q</div><div><div class='brand-title'>QuantX</div><div class='brand-sub'>Financial Intelligence</div></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-label' style='margin-top:1.2rem;'>Explore</div>", unsafe_allow_html=True)
        pages = [
            ("app.py", "Home", ":material/home:"),
            ("pages/1_📈_Markets.py", "Markets", ":material/show_chart:"),
            ("pages/2_🧠_Strategies.py", "Strategies", ":material/psychology:"),
            ("pages/3_🔬_Backtesting.py", "Backtesting", ":material/science:"),
            ("pages/4_⚠️_Risk_Analysis.py", "Risk analysis", ":material/warning:"),
            ("pages/5_🤖_AI_Insights.py", "AI insights", ":material/smart_toy:"),
        ]
        for path, label, icon in pages:
            if label == active_page:
                st.markdown(f"**{icon} {label}**")
            else:
                st.page_link(path, label=label, icon=icon)


@st.cache_data(ttl=900, show_spinner=False)
def load_asset_data(asset_name: str) -> pd.DataFrame:
    data = load_data(ASSET_TICKERS[asset_name])
    data = calculate_sma(data, period=20)
    data = calculate_ema(data, period=20)
    data = calculate_returns(data)
    return calculate_volatility(data, period=20)


def apply_strategy(data: pd.DataFrame, strategy_name: str) -> pd.DataFrame:
    if strategy_name == "SMA Crossover":
        return sma_crossover_strategy(data, short_window=20, long_window=50)
    if strategy_name == "EMA Trend":
        return ema_trend_strategy(data, ema_window=20)
    if strategy_name == "Momentum":
        return momentum_strategy(data, momentum_window=10)
    if strategy_name == "Mean Reversion":
        return mean_reversion_strategy(data, window=20, threshold=0.02)
    raise ValueError(f"Unknown strategy: {strategy_name}")


def signal_points(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    changes = data["Signal"].diff().fillna(data["Signal"])
    buys = data[(data["Signal"] == 1) & (changes != 0)]
    sells = data[(data["Signal"] == -1) & (changes != 0)]
    return buys, sells


def signal_label(value: int) -> str:
    return {1: "BUY", -1: "SELL", 0: "HOLD"}.get(int(value), "HOLD")


def signal_summary(data: pd.DataFrame) -> dict[str, object]:
    buys, sells = signal_points(data)
    latest_signal = int(data["Signal"].iloc[-1])
    return {
        "buy_count": len(buys),
        "sell_count": len(sells),
        "hold_count": int((data["Signal"] == 0).sum()),
        "latest": signal_label(latest_signal),
        "last_buy": buys.index[-1] if not buys.empty else None,
        "last_sell": sells.index[-1] if not sells.empty else None,
    }


def add_signal_traces(fig: go.Figure, data: pd.DataFrame, strategy_name: str = "Selected strategy") -> None:
    buys, sells = signal_points(data)
    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys.index,
            y=buys["Close"],
            mode="markers",
            name="BUY",
            marker={"color": "#4ade80", "symbol": "triangle-up", "size": 11, "line": {"color": "#d9ffe6", "width": 1}},
            customdata=[strategy_name] * len(buys),
            hovertemplate="BUY SIGNAL<br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:,.2f}<br>Strategy: %{customdata}<extra></extra>",
        ))
    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells.index,
            y=sells["Close"],
            mode="markers",
            name="SELL",
            marker={"color": "#ff5f7a", "symbol": "triangle-down", "size": 11, "line": {"color": "#ffd6df", "width": 1}},
            customdata=[strategy_name] * len(sells),
            hovertemplate="SELL SIGNAL<br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:,.2f}<br>Strategy: %{customdata}<extra></extra>",
        ))


def chart_layout(height: int = 430) -> dict:
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(13,23,38,.9)",
        "height": height,
        "margin": {"l": 8, "r": 8, "t": 18, "b": 8},
        "hovermode": "x unified",
        "font": {"color": "#edf6ff"},
        "xaxis": {
            "showgrid": True,
            "gridcolor": "rgba(148,163,184,.12)",
            "zeroline": False,
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1M", "step": "month", "stepmode": "backward"},
                    {"count": 6, "label": "6M", "step": "month", "stepmode": "backward"},
                    {"count": 1, "label": "YTD", "step": "year", "stepmode": "todate"},
                    {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                    {"count": 5, "label": "5Y", "step": "year", "stepmode": "backward"},
                    {"label": "ALL", "step": "all"},
                ],
                "bgcolor": "rgba(14,25,44,.9)",
                "activecolor": "#3a86ff",
                "font": {"color": "#edf6ff"},
            },
        },
        "yaxis": {"showgrid": True, "gridcolor": "rgba(148,163,184,.12)", "zeroline": False},
    }


def run_backtest(
    asset_name: str,
    strategy_name: str,
    initial_capital: float,
    transaction_cost_percent: float,
    position_size: float,
) -> tuple[pd.DataFrame, pd.DataFrame, dict, Backtester]:
    from src.metrics import calculate_metrics

    source_data = load_asset_data(asset_name)
    strategy_data = apply_strategy(source_data, strategy_name)
    strategy_data["signal"] = strategy_data["Signal"]
    backtester = Backtester(
        initial_capital=float(initial_capital),
        position_size=float(position_size),
        transaction_cost=float(transaction_cost_percent) / 100,
    )
    result = backtester.run(strategy_data)
    result["Date"] = pd.to_datetime(strategy_data.index).to_numpy()
    equity_curve = pd.Series(result["portfolio_value"].to_numpy(), index=result["Date"], name="portfolio_value")
    metrics = calculate_metrics(equity_curve, benchmark_prices=strategy_data["Close"])
    return strategy_data, result, metrics, backtester


def aligned_comparison(result: pd.DataFrame, strategy_data: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
    strategy = result.set_index("Date")["portfolio_value"].rename("Strategy")
    benchmark = strategy_data["Close"].copy()
    benchmark.index = pd.to_datetime(benchmark.index)
    aligned = pd.concat([strategy, benchmark.rename("Close")], axis=1, join="inner").dropna()
    if aligned.empty:
        raise ValueError("No overlapping dates are available for the comparison.")
    aligned["Buy & Hold"] = aligned["Close"].div(aligned["Close"].iloc[0]).mul(initial_capital)
    return aligned[["Strategy", "Buy & Hold"]].reset_index(names="Date")


def add_price_trace(fig: go.Figure, data: pd.DataFrame) -> None:
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close", line={"color": "#8ec5ff", "width": 2.3}))
