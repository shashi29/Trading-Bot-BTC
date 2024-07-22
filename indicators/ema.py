import pandas as pd

def calculate_ema(df, period=50):
    df['EMA'] = df['Close'].ewm(span=period, adjust=False).mean()
    # Calculate EMA slope
    df['EMA_Slope'] = df['EMA'].diff()    
    # Check if EMA slope is positive
    df['EMA_Slope_Up'] = df['EMA_Slope'] > 0
    return df

def calculate_ema_ripple(data, period=50):
    """
    Calculate EMA of the specified period and determine ripple and FBD signals.

    Args:
        data (pd.DataFrame): DataFrame containing OHLC data.
        period (int): The period for calculating the EMA.

    Returns:
        pd.DataFrame: DataFrame with added EMA, ripple, and FBD signal columns.
    """
    # Calculate Exponential Moving Average (EMA) of the specified period
    data['EMA_50'] = data['Close'].ewm(span=period, adjust=False).mean()

    # Step 1: Identify HA Close Price Above 50 EMA
    data['Price_Above_EMA'] = data['HA_Close'] > data['EMA_50']

    # Handle Fake Break Down (FBD) Signal
    data['FBD_Signal'] = (data['Price_Above_EMA'].shift(1).fillna(False).astype(bool)) & (~data['Price_Above_EMA'].astype(bool))

    return data