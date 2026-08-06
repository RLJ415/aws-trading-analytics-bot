import pandas as pd


def calculate_rsi(df, period=14):
    """
    Calculates the Relative Strength Index (RSI).

    Parameters:
        df: Pandas DataFrame containing a 'Close' column.
        period: Number of periods used to calculate RSI.

    Returns:
        Pandas Series containing RSI values.
    """

    delta = df["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi