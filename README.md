# QuantX — Quantitative Multi-Asset Financial Intelligence & Backtesting Platform

QuantX is a quantitative finance and FinTech research platform that analyzes historical market data across multiple asset classes and evaluates quantitative trading strategies through realistic backtesting.

The platform combines financial data engineering, technical indicators, risk analysis, correlation analysis, strategy generation, portfolio backtesting, benchmark comparison, interactive visualization, and AI-powered insights in a unified dashboard.

---

## 🚀 Problem Statement

Financial markets generate large amounts of historical data across commodities, cryptocurrencies, and equities.

Investors and researchers need to:

- Analyze historical market behavior
- Compare different assets
- Measure risk and volatility
- Identify relationships between assets
- Test quantitative trading strategies
- Compare strategy performance with Buy & Hold
- Understand how strategies behave under different market conditions

QuantX provides a unified platform to perform these tasks using historical market data and quantitative analysis.

---

## 🎯 Objectives

The main objectives of QuantX are:

- Collect and normalize historical financial data
- Analyze asset price behavior
- Calculate quantitative indicators
- Measure investment risk
- Analyze correlations between assets
- Generate quantitative trading signals
- Backtest trading strategies
- Include transaction costs and position sizing
- Compare strategies with Buy & Hold
- Visualize portfolio performance
- Provide AI-assisted quantitative insights

---

## 📊 Supported Assets

QuantX currently analyzes:

| Asset | Data Source | Ticker |
|---|---|---|
| 🥇 Gold | Yahoo Finance | `GC=F` |
| ₿ Bitcoin | Yahoo Finance | `BTC-USD` |
| 🟢 NVIDIA | Yahoo Finance | `NVDA` |

Historical market data is retrieved using `yfinance`.

---

## 📈 Quantitative Analysis

QuantX calculates several important financial indicators.

### Moving Averages

- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)

### Returns

- Daily Returns
- Cumulative Returns

### Risk Metrics

- Historical Volatility
- Annualized Volatility
- Sharpe Ratio
- Maximum Drawdown

### Correlation Analysis

- Cross-asset correlation matrix
- Rolling correlation analysis

These metrics help users understand asset performance, risk, and relationships.

---

## 🧠 Trading Strategies

QuantX supports multiple quantitative strategies.

### 1. SMA Crossover

Uses short-term and long-term Simple Moving Averages to generate trading signals.

```text
Short SMA > Long SMA → BUY
Short SMA < Long SMA → SELL