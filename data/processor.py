# data/processor.py

import pandas as pd
import numpy as np

def calculate_heikin_ashi(df):
    """
    Calculate Heikin Ashi candles from OHLC data.
    
    Args:
    - df (pd.DataFrame): DataFrame containing 'Open', 'High', 'Low', 'Close' columns
    
    Returns:
    - pd.DataFrame: DataFrame with added Heikin Ashi columns
    """
    df = df.copy()
    df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    df['HA_Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
    df.loc[0, 'HA_Open'] = df['Open'].iloc[0]
    df['HA_High'] = df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    df['HA_Low'] = df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)
    df['HA_Type'] = df.apply(classify_candle, axis=1)
    df['HA_Green'] = df['HA_Type'].str.contains(r"Solid Green|Neutral")
    df['HA_Red'] = df['HA_Type'].str.contains(r"Solid Red|Neutral")
    #Bullish pattern
    df = add_candlestick_patterns(df)
    return df

def classify_candle(row):
    """
    Classify the type of Heikin Ashi candle.
    
    Args:
    - row (pd.Series): A row from the DataFrame containing HA_Open, HA_Close, HA_High, HA_Low
    
    Returns:
    - str: The classification of the candle
    """
    if row["HA_Open"] == row["HA_Low"] and row["HA_Close"] > row["HA_Open"]:
        return "Solid Green"
    elif row["HA_Open"] == row["HA_High"] and row["HA_Close"] < row["HA_Open"]:
        return "Solid Red"
    elif row["HA_High"] != max(row["HA_Close"], row["HA_Open"]) or row["HA_Low"] != min(row["HA_Close"], row["HA_Open"]):
        return "Neutral"
    else:
        return "Unknown"

def add_candlestick_patterns(df):
    """
    Add candlestick pattern identifications to the DataFrame.
    
    Args:
    - df (pd.DataFrame): DataFrame containing OHLC data
    
    Returns:
    - pd.DataFrame: DataFrame with added 'Pattern' column
    """
    df['Pattern'] = np.nan
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_bullish_engulfing(df)))
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_morning_star(df)))
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_three_white_soldiers(df)))
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_hammer(df)))
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_bullish_harami(df)))
    df['Pattern'] = df['Pattern'].combine_first(pd.Series(detect_bullish_piercing(df)))
    return df

def detect_bullish_engulfing(df):
    """
    Detects Bullish Engulfing patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Bullish Engulfing patterns are detected.
    """
    bullish_engulfing = []
    
    for i in range(1, len(df)):
        prev_open, prev_close = df['Open'][i-1], df['Close'][i-1]
        curr_open, curr_close = df['Open'][i], df['Close'][i]
        
        # Bullish Engulfing Pattern criteria
        if prev_close < prev_open and curr_close > curr_open and curr_close > prev_open and curr_open < prev_close:
            bullish_engulfing.append('Bullish Engulfing')
        else:
            bullish_engulfing.append(np.nan)
    
    return bullish_engulfing

def detect_morning_star(df):
    """
    Detects Morning Star patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Morning Star patterns are detected.
    """
    morning_star = []
    
    for i in range(2, len(df)):
        prev1_open, prev1_close, prev1_low = df['Open'].iloc[i-2], df['Close'].iloc[i-2], df['Low'].iloc[i-2]
        prev2_open, prev2_close, prev2_low = df['Open'].iloc[i-1], df['Close'].iloc[i-1], df['Low'].iloc[i-1]
        curr_open, curr_close, curr_high = df['Open'].iloc[i], df['Close'].iloc[i], df['High'].iloc[i]
        
        # Morning Star Pattern criteria
        if (prev1_close < prev1_open and abs(prev1_close - prev1_open) > (prev1_open - prev1_low) * 2 and
            prev2_close < prev2_open and abs(prev2_close - prev2_open) < (prev2_open - prev2_low) * 2 and
            curr_close > curr_open and abs(curr_close - curr_open) > (curr_high - curr_close) * 2):
            morning_star.append('Morning Star')
        else:
            morning_star.append(np.nan)
    
    return morning_star

def detect_three_white_soldiers(df):
    """
    Detects Three White Soldiers patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Three White Soldiers patterns are detected.
    """
    three_white_soldiers = []
    
    for i in range(2, len(df)):
        prev1_open, prev1_close = df['Open'][i-2], df['Close'][i-2]
        prev2_open, prev2_close = df['Open'][i-1], df['Close'][i-1]
        curr_open, curr_close = df['Open'][i], df['Close'][i]
        
        # Three White Soldiers Pattern criteria
        if (prev1_close > prev1_open and prev2_close > prev2_open and curr_close > curr_open and
            prev1_close > prev1_open and prev2_close > prev2_open and curr_close > curr_open):
            three_white_soldiers.append('Three White Soldiers')
        else:
            three_white_soldiers.append(np.nan)
    
    return three_white_soldiers

def detect_hammer(df):
    """
    Detects Hammer patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Hammer patterns are detected.
    """
    hammer = []
    
    for i in range(len(df)):
        open_price, close_price = df['Open'][i], df['Close'][i]
        high_price, low_price = df['High'][i], df['Low'][i]
        
        # Hammer Pattern criteria
        if (close_price > open_price and (high_price - low_price) > 2 * (close_price - open_price) and
            (open_price - low_price) / (0.001 + high_price - low_price) > 0.6):
            hammer.append('Hammer')
        else:
            hammer.append(np.nan)
    
    return hammer

def detect_bullish_harami(df):
    """
    Detects Bullish Harami patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Bullish Harami patterns are detected.
    """
    bullish_harami = []
    
    for i in range(1, len(df)):
        prev_open, prev_close = df['Open'][i-1], df['Close'][i-1]
        curr_open, curr_close = df['Open'][i], df['Close'][i]
        
        # Bullish Harami Pattern criteria
        if prev_close < prev_open and curr_close > curr_open and curr_open > prev_close and curr_close < prev_open:
            bullish_harami.append('Bullish Harami')
        else:
            bullish_harami.append(np.nan)
    
    return bullish_harami

def detect_bullish_piercing(df):
    """
    Detects Bullish Piercing patterns in the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        list: A list indicating where Bullish Piercing patterns are detected.
    """
    bullish_piercing = []
    
    for i in range(1, len(df)):
        prev_open, prev_close = df['Open'][i-1], df['Close'][i-1]
        curr_open, curr_close = df['Open'][i], df['Close'][i]
        
        # Bullish Piercing Pattern criteria
        if prev_close < prev_open and curr_close > curr_open and curr_close > (prev_close + prev_open) / 2:
            bullish_piercing.append('Bullish Piercing')
        else:
            bullish_piercing.append(np.nan)
    
    return bullish_piercing
