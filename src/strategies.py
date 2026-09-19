import pandas as pd


def sma_crossover_strategy(data, short_window=20, long_window=50):
    """
    Generate BUY, SELL, HOLD signals using SMA crossover.
    """

    df = data.copy()

    df["SMA_Short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_Long"] = df["Close"].rolling(window=long_window).mean()

    df["Signal"] = 0

    df.loc[df["SMA_Short"] > df["SMA_Long"], "Signal"] = 1
    df.loc[df["SMA_Short"] < df["SMA_Long"], "Signal"] = -1

    return df
def ema_trend_strategy(data, ema_window=20):
    """
    Generate BUY, SELL, HOLD signals using EMA trend.
    """

    df = data.copy()

    df["EMA"] = df["Close"].ewm(span=ema_window, adjust=False).mean()

    df["Signal"] = 0

    df.loc[df["Close"] > df["EMA"], "Signal"] = 1
    df.loc[df["Close"] < df["EMA"], "Signal"] = -1

    return df
def momentum_strategy(data, momentum_window=10):
    """
    Generate BUY, SELL, HOLD signals using price momentum.
    """

    df = data.copy()

    df["Momentum"] = df["Close"].diff(momentum_window)

    df["Signal"] = 0

    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    return df
def mean_reversion_strategy(data, window=20, threshold=0.02):
    """
    Generate BUY, SELL, HOLD signals using mean reversion.
    """

    df = data.copy()

    df["Mean"] = df["Close"].rolling(window=window).mean()

    df["Deviation"] = (df["Close"] - df["Mean"]) / df["Mean"]

    df["Signal"] = 0

    df.loc[df["Deviation"] < -threshold, "Signal"] = 1
    df.loc[df["Deviation"] > threshold, "Signal"] = -1

    return df