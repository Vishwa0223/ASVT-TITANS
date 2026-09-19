import pandas as pd


class Backtester:
    def __init__(self, initial_capital: float = 100000, position_size: float = 1.0,
                 transaction_cost: float = 0.001):
        """
        Parameters
        ----------
        initial_capital : float
            Starting cash for the portfolio (e.g. 100000).
        position_size : float
            Fraction of available capital to use per trade (1.0 = 100%).
        transaction_cost : float
            Cost per trade as a fraction (0.001 = 0.1% per buy/sell).
        """
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.transaction_cost = transaction_cost

        # These get filled in after run() is called
        self.trades = []
        self.equity_curve = None
        self.results_df = None

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Run the backtest on the given data.

        data must have columns: 'Close' and 'signal'

        Returns
        -------
        pd.DataFrame with columns:
            Close, signal, position, cash, holdings, portfolio_value
        """
        df = data.copy()
        df = df.reset_index(drop=True)

        cash = self.initial_capital
        shares_held = 0
        position = 0  # 0 = flat, 1 = long

        cash_list = []
        holdings_list = []
        portfolio_value_list = []
        position_list = []

        self.trades = []  # reset trades log

        for i, row in df.iterrows():
            price = row['Close']
            signal = row['signal']

            # --- BUY ---
            if signal == 1 and position == 0:
                capital_to_use = cash * self.position_size
                cost = capital_to_use * self.transaction_cost
                capital_to_use -= cost
                shares_held = capital_to_use / price
                cash -= (shares_held * price + cost)
                position = 1

                self.trades.append({
                    'index': i,
                    'type': 'BUY',
                    'price': price,
                    'shares': shares_held,
                    'cost': cost
                })

            # --- SELL ---
            elif signal == -1 and position == 1:
                proceeds = shares_held * price
                cost = proceeds * self.transaction_cost
                proceeds -= cost
                cash += proceeds

                self.trades.append({
                    'index': i,
                    'type': 'SELL',
                    'price': price,
                    'shares': shares_held,
                    'cost': cost
                })

                shares_held = 0
                position = 0

            # --- Track portfolio value each day ---
            holdings_value = shares_held * price
            total_value = cash + holdings_value

            cash_list.append(cash)
            holdings_list.append(holdings_value)
            portfolio_value_list.append(total_value)
            position_list.append(position)

        df['position'] = position_list
        df['cash'] = cash_list
        df['holdings'] = holdings_list
        df['portfolio_value'] = portfolio_value_list

        self.equity_curve = df['portfolio_value']
        self.results_df = df

        return df

    def get_trade_log(self) -> pd.DataFrame:
        """Returns all executed trades as a DataFrame."""
        return pd.DataFrame(self.trades)

    def get_num_trades(self) -> int:
        """Returns number of completed trades (BUY + SELL both count)."""
        return len(self.trades)

    def get_equity_curve(self) -> pd.Series:
        """Returns the portfolio value over time."""
        return self.equity_curve

    def get_final_value(self) -> float:
        """Returns the final portfolio value at the end of the backtest."""
        if self.equity_curve is not None:
            return self.equity_curve.iloc[-1]
        return self.initial_capital


# Quick manual test (only runs if you execute this file directly)
if __name__ == "__main__":
    # Fake sample data just to check the code works
    sample_data = pd.DataFrame({
        'Close': [100, 102, 101, 105, 110, 108, 115, 113, 120, 118],
        'signal': [1, 0, 0, 0, -1, 1, 0, 0, -1, 0]
    })

    bt = Backtester(initial_capital=100000)
    result = bt.run(sample_data)

    print(result)
    print("\nTrade Log:")
    print(bt.get_trade_log())
    print("\nFinal Portfolio Value:", bt.get_final_value())
    print("Number of Trades:", bt.get_num_trades())
