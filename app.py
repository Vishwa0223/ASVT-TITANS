import os
import streamlit as st
import pandas as pd

from src.data_loader import load_data

from src.indicators import (
    calculate_sma,
    calculate_ema,
    calculate_returns,
    calculate_volatility,
    calculate_correlation,
    calculate_rolling_correlation,
)

from src.strategies import (
    sma_crossover_strategy,
    ema_trend_strategy,
    momentum_strategy,
    mean_reversion_strategy,
)

from src.backtest import Backtester
from src.metrics import calculate_metrics


from src.ai_analysis import analyze_market




# =
# PAGE CONFIGURATION
# =

st.set_page_config(
    page_title="ASVT TITANS",
    page_icon="📊",
    layout="wide"
)


# =
# TITLE
# =

st.title("ASVT TITANS")

st.subheader(
    "Multi-Asset Quantitative Trading & Risk Analytics"
)


# =
# ASSET TICKERS
# =

asset_tickers = {
    "Gold": "GC=F",
    "Bitcoin": "BTC-USD",
    "NVIDIA": "NVDA"
}


# =
# SIDEBAR
# =

st.sidebar.header("Dashboard Settings")


asset = st.sidebar.selectbox(
    "Select Asset",
    [
        "Gold",
        "Bitcoin",
        "NVIDIA"
    ]
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


transaction_cost_percent = st.sidebar.number_input(
    "Transaction Cost (%)",
    min_value=0.0,
    value=0.1,
    step=0.01
)


# =
# LOAD SELECTED ASSET DATA
# =

ticker = asset_tickers[asset]

st.info(
    f"Loading historical data for {asset}..."
)

try:

    data = load_data(ticker)

    data = calculate_sma(
        data,
        period=20
    )

    data = calculate_ema(
        data,
        period=20
    )

    data = calculate_returns(
        data
    )

    data = calculate_volatility(
        data,
        period=20
    )

except Exception as e:

    st.error(
        f"Unable to load market data: {e}"
    )

    st.stop()


# =
# APPLY SELECTED STRATEGY
# =

if strategy == "SMA Crossover":

    strategy_data = sma_crossover_strategy(
        data,
        short_window=20,
        long_window=50
    )


elif strategy == "EMA Trend":

    strategy_data = ema_trend_strategy(
        data,
        ema_window=20
    )


elif strategy == "Momentum":

    strategy_data = momentum_strategy(
        data,
        momentum_window=10
    )


elif strategy == "Mean Reversion":

    strategy_data = mean_reversion_strategy(
        data,
        window=20,
        threshold=0.02
    )


else:

    strategy_data = data.copy()


# =
# CURRENT SELECTION
# =

st.write("### Current Selection")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Asset",
        asset
    )


with col2:

    st.metric(
        "Strategy",
        strategy
    )


with col3:

    st.metric(
        "Initial Capital",
        f"${initial_capital:,.2f}"
    )


with col4:

    st.metric(
        "Transaction Cost",
        f"{transaction_cost_percent}%"
    )


# =
# MARKET DATA
# =

st.write("### Market Data")


latest_price = float(
    strategy_data["Close"].iloc[-1]
)


previous_price = float(
    strategy_data["Close"].iloc[-2]
)


price_change = (
    latest_price - previous_price
)


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


# =
# PRICE CHART
# =

st.write(
    "### Price & Moving Averages"
)


chart_columns = [
    "Close"
]


if "SMA" in strategy_data.columns:

    chart_columns.append(
        "SMA"
    )


if "EMA" in strategy_data.columns:

    chart_columns.append(
        "EMA"
    )


chart_data = strategy_data[
    chart_columns
].dropna()


st.line_chart(
    chart_data
)


# =
# STRATEGY SIGNAL
# =

st.write(
    "### Strategy Signal"
)


latest_signal = int(
    strategy_data["Signal"].iloc[-1]
)


if latest_signal == 1:

    st.success(
        "🟢 BUY Signal"
    )


elif latest_signal == -1:

    st.error(
        "🔴 SELL Signal"
    )


else:

    st.warning(
        "🟡 HOLD Signal"
    )


# =
# BACKTEST
# =

st.write(
    "### Backtesting"
)


backtest_data = strategy_data.copy()


# Backtester expects lowercase "signal"

backtest_data["signal"] = (
    backtest_data["Signal"]
)


# Convert percentage to decimal
# 0.1% -> 0.001

transaction_cost = (
    transaction_cost_percent / 100
)


try:

    backtester = Backtester(
        initial_capital=initial_capital,
        position_size=1.0,
        transaction_cost=transaction_cost
    )


    backtest_result = backtester.run(
        backtest_data
    )


except Exception as e:

    st.error(
        f"Backtest failed: {e}"
    )

    st.stop()


# =
# PERFORMANCE METRICS
# =

st.write(
    "### Performance Metrics"
)


equity_curve = (
    backtester.get_equity_curve()
)


metrics = calculate_metrics(
    equity_curve,
    benchmark_prices=backtest_data["Close"]
)


metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)


with metric_col1:

    st.metric(
        "Total Return",
        f"{metrics['Total Return (%)']:.2f}%"
    )


with metric_col2:

    st.metric(
        "Sharpe Ratio",
        f"{metrics['Sharpe Ratio']:.2f}"
    )


with metric_col3:

    st.metric(
        "Volatility",
        f"{metrics['Volatility (%)']:.2f}%"
    )


with metric_col4:

    st.metric(
        "Max Drawdown",
        f"{metrics['Max Drawdown (%)']:.2f}%"
    )


# =
# BUY & HOLD COMPARISON
# =

st.write(
    "### Strategy vs Buy & Hold"
)


benchmark_col1, benchmark_col2 = st.columns(2)


with benchmark_col1:

    st.metric(
        "Buy & Hold Return",
        f"{metrics['Buy & Hold Return (%)']:.2f}%"
    )


with benchmark_col2:

    st.metric(
        "Strategy vs Buy & Hold",
        f"{metrics['Strategy vs Buy & Hold (%)']:.2f}%"
    )


# =
# EQUITY CURVE
# =

st.write(
    "### Portfolio Equity Curve"
)


equity_chart = backtest_result[
    ["portfolio_value"]
].copy()


st.line_chart(
    equity_chart
)


# =
# TRADING ACTIVITY
# =

st.write(
    "### Trading Activity"
)


trade_col1, trade_col2 = st.columns(2)


with trade_col1:

    st.metric(
        "Number of Trades",
        backtester.get_num_trades()
    )


with trade_col2:

    st.metric(
        "Final Portfolio Value",
        f"${backtester.get_final_value():,.2f}"
    )


# =
# TRADE LOG
# =

trade_log = (
    backtester.get_trade_log()
)


if not trade_log.empty:

    st.write(
        "### Trade Log"
    )


    st.dataframe(
        trade_log,
        use_container_width=True
    )


else:

    st.info(
        "No trades were executed during "
        "the selected period."
    )


# =
# RECENT STRATEGY DATA
# =

st.write(
    "### Recent Strategy Data"
)


display_columns = [
    "Close",
    "Signal",
    "Daily_Return",
    "Cumulative_Return",
    "Volatility",
    "Annualized_Volatility"
]


if "SMA_Short" in strategy_data.columns:

    display_columns.append(
        "SMA_Short"
    )


if "SMA_Long" in strategy_data.columns:

    display_columns.append(
        "SMA_Long"
    )


if "Momentum" in strategy_data.columns:

    display_columns.append(
        "Momentum"
    )


if "Mean" in strategy_data.columns:

    display_columns.append(
        "Mean"
    )


if "Deviation" in strategy_data.columns:

    display_columns.append(
        "Deviation"
    )


st.dataframe(
    strategy_data[
        display_columns
    ].tail(10),
    use_container_width=True
)


# =
# MULTI-ASSET CORRELATION
# =

st.write(
    "## 📊 Multi-Asset Correlation Analysis"
)


st.write(
    "Correlation between Gold, Bitcoin and NVIDIA "
    "based on daily returns."
)


try:

    gold_data = load_data(
        "GC=F"
    )

    bitcoin_data = load_data(
        "BTC-USD"
    )

    nvidia_data = load_data(
        "NVDA"
    )


    multi_asset_prices = pd.DataFrame({

        "Gold": gold_data["Close"],

        "Bitcoin": bitcoin_data["Close"],

        "NVIDIA": nvidia_data["Close"]

    }).dropna()


    correlation_matrix = calculate_correlation(
        multi_asset_prices
    )


    st.write(
        "### Correlation Matrix"
    )


    st.dataframe(
        correlation_matrix.style.format(
            "{:.2f}"
        ).background_gradient(
            cmap="RdBu",
            vmin=-1,
            vmax=1
        ),
        use_container_width=True
    )


except Exception as e:

    st.error(
        f"Correlation analysis failed: {e}"
    )


# =
# ROLLING CORRELATION
# =

st.write(
    "### Rolling Correlation"
)


try:

    rolling_pairs = {

        "Gold vs Bitcoin":
            multi_asset_prices["Gold"].rolling(
                30
            ).corr(
                multi_asset_prices["Bitcoin"]
            ),

        "Gold vs NVIDIA":
            multi_asset_prices["Gold"].rolling(
                30
            ).corr(
                multi_asset_prices["NVIDIA"]
            ),

        "Bitcoin vs NVIDIA":
            multi_asset_prices["Bitcoin"].rolling(
                30
            ).corr(
                multi_asset_prices["NVIDIA"]
            )
    }


    selected_pair = st.selectbox(
        "Select Correlation Pair",
        list(rolling_pairs.keys())
    )


    selected_rolling = (
        rolling_pairs[selected_pair]
        .dropna()
        .rename("Correlation")
    )


    st.line_chart(
        selected_rolling
    )


except Exception as e:

    st.error(
        f"Rolling correlation failed: {e}"
    )


# =
# AI MARKET ANALYSIS
# =

st.write(
    "### 🤖 AI Market Analysis"
)


if st.button(
    "Analyze Market with AI"
):

    # Check API key before importing AI module

    if not os.getenv("OPENAI_API_KEY"):

        st.warning(
            "AI analysis is currently unavailable. "
            "An OpenAI API key is required."
        )

    else:

        try:

            from src.ai_analysis import analyze_market


            latest_return = (
                float(
                    strategy_data[
                        "Daily_Return"
                    ].iloc[-1]
                )
                * 100
            )


            latest_volatility = (
                float(
                    strategy_data[
                        "Annualized_Volatility"
                    ].iloc[-1]
                )
                * 100
            )


            total_return = (
                metrics[
                    "Total Return (%)"
                ]
            )


            sharpe = (
                metrics[
                    "Sharpe Ratio"
                ]
            )


            max_drawdown = (
                metrics[
                    "Max Drawdown (%)"
                ]
            )


            buy_hold_return = (
                metrics[
                    "Buy & Hold Return (%)"
                ]
            )


            strategy_vs_bh = (
                metrics[
                    "Strategy vs Buy & Hold (%)"
                ]
            )


            prompt = f"""
Analyze the following historical
market backtest results.

Asset: {asset}

Strategy: {strategy}

Latest Daily Return:
{latest_return:.2f}%

Annualized Volatility:
{latest_volatility:.2f}%

Total Strategy Return:
{total_return:.2f}%

Sharpe Ratio:
{sharpe:.2f}

Maximum Drawdown:
{max_drawdown:.2f}%

Buy and Hold Return:
{buy_hold_return:.2f}%

Strategy vs Buy and Hold:
{strategy_vs_bh:.2f}%

Give a short quantitative interpretation
covering:

1. Market performance
2. Risk level
3. Strategy performance
4. Strategy versus Buy and Hold
5. Important caution about historical
   backtesting

Do not claim that historical performance
guarantees future returns.
"""


            with st.spinner(
                "AI is analyzing the market..."
            ):

                ai_result = analyze_market(
                    prompt
                )


            st.success(
                "AI Analysis Complete"
            )


            st.write(
                ai_result
            )


        except Exception as e:

            st.error(
                f"AI analysis failed: {e}"
            )


# =
# FOOTER
# =

st.info(
    "Historical market data is used for "
    "quantitative analysis. Past performance "
    "does not guarantee future returns."
)
