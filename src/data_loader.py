import yfinance as yf


def load_data(ticker, start="2020-01-01"):
    data = yf.download(ticker, start=start, auto_adjust=False)

    data = data.dropna()

    if hasattr(data.columns, "levels"):
        data.columns = data.columns.get_level_values(0)

    data.index.name = "Date"

    return data