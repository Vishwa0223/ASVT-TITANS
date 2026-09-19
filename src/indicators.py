def calculate_sma(data, period=20):
    data = data.copy()
    data["SMA"] = data["Close"].rolling(window=period).mean()
    return data
def calculate_ema(data, period=20):
    data = data.copy()
    data["EMA"] = data["Close"].ewm(span=period, adjust=False).mean()
    return data
def calculate_returns(data):
    data = data.copy()

    data["Daily_Return"] = data["Close"].pct_change()

    data["Cumulative_Return"] = (1 + data["Daily_Return"]).cumprod() - 1

    return data
def calculate_volatility(data, period=20):
    data = data.copy()

    data["Volatility"] = data["Daily_Return"].rolling(window=period).std()

    data["Annualized_Volatility"] = data["Volatility"] * (252 ** 0.5)

    return data
def calculate_correlation(data):
    return data.pct_change().corr()


def calculate_rolling_correlation(data, window=30):
    returns = data.pct_change()
    return returns.rolling(window=window).corr()