"""
metrics.py
Member 3 - Performance Metrics

This module takes the equity curve (portfolio value over time) produced by
backtest.py and calculates standard performance metrics used to judge a
trading strategy.

Main function:
    calculate_metrics(equity_curve, benchmark_prices=None) -> dict
"""

import numpy as np
import pandas as pd


def total_return(equity_curve: pd.Series) -> float:
    """Overall % return from start to end of the backtest."""
    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]
    return (end_value - start_value) / start_value * 100


def daily_returns(equity_curve: pd.Series) -> pd.Series:
    """Day-over-day percentage change of the portfolio."""
    return equity_curve.pct_change().dropna()


def sharpe_ratio(equity_curve: pd.Series, risk_free_rate: float = 0.0,
                  periods_per_year: int = 252) -> float:
    """
    Sharpe Ratio = (mean return - risk free rate) / std dev of returns,
    annualized.

    periods_per_year = 252 for daily trading data (typical trading days/year)
    """
    returns = daily_returns(equity_curve)
    if returns.std() == 0 or len(returns) == 0:
        return 0.0

    excess_returns = returns - (risk_free_rate / periods_per_year)
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(periods_per_year)
    return sharpe


def volatility(equity_curve: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized volatility (standard deviation of returns) as a %."""
    returns = daily_returns(equity_curve)
    return returns.std() * np.sqrt(periods_per_year) * 100


def max_drawdown(equity_curve: pd.Series) -> float:
    """
    Maximum Drawdown: the biggest drop (%) from a peak to a later low
    in the portfolio value.
    """
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown.min() * 100  # negative number, e.g. -18.5%


def buy_and_hold_return(prices: pd.Series) -> float:
    """
    Simple Buy & Hold return: what you'd get if you just bought at the
    start and held till the end, no trading at all.
    """
    start_price = prices.iloc[0]
    end_price = prices.iloc[-1]
    return (end_price - start_price) / start_price * 100


def calculate_metrics(equity_curve: pd.Series, benchmark_prices: pd.Series = None) -> dict:
    """
    Calculate all key performance metrics in one call.

    Parameters
    ----------
    equity_curve : pd.Series
        Portfolio value over time (from Backtester.get_equity_curve()).
    benchmark_prices : pd.Series, optional
        The raw 'Close' price series, used for Buy & Hold comparison.

    Returns
    -------
    dict of all metrics, ready to print or show on the dashboard.
    """
    results = {
        'Total Return (%)': round(total_return(equity_curve), 2),
        'Sharpe Ratio': round(sharpe_ratio(equity_curve), 2),
        'Volatility (%)': round(volatility(equity_curve), 2),
        'Max Drawdown (%)': round(max_drawdown(equity_curve), 2),
    }

    if benchmark_prices is not None:
        bh_return = buy_and_hold_return(benchmark_prices)
        results['Buy & Hold Return (%)'] = round(bh_return, 2)
        results['Strategy vs Buy & Hold (%)'] = round(
            results['Total Return (%)'] - bh_return, 2
        )

    return results


# Quick manual test (only runs if you execute this file directly)
if __name__ == "__main__":
    # Fake equity curve just to check the code works
    equity = pd.Series([100000, 101000, 99500, 103000, 107000, 105000, 110000])
    prices = pd.Series([100, 101, 99.5, 103, 107, 105, 110])

    metrics = calculate_metrics(equity, benchmark_prices=prices)

    print("Performance Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
