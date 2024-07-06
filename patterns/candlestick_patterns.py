# patterns/candlestick_patterns.py

import numpy as np
import pandas as pd

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
        prev_open, prev_close = df['Open'].iloc[i-1], df['Close'].iloc[i-1]
        curr_open, curr_close = df['Open'].iloc[i], df['Close'].iloc[i]
        
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
        prev1_open, prev1_close = df['Open'].iloc[i-2], df['Close'].iloc[i-2]
        prev2_open, prev2_close = df['Open'].iloc[i-1], df['Close'].iloc[i-1]
        curr_open, curr_close = df['Open'].iloc[i], df['Close'].iloc[i]
        
        if (prev1_close > prev1_open and prev2_close > prev2_open and curr_close > curr_open and
            prev2_open > prev1_close and curr_open > prev2_close):
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
        open_price, close_price = df['Open'].iloc[i], df['Close'].iloc[i]
        high_price, low_price = df['High'].iloc[i], df['Low'].iloc[i]
        
        body = abs(close_price - open_price)
        lower_wick = min(open_price, close_price) - low_price
        upper_wick = high_price - max(open_price, close_price)
        
        if (lower_wick > 2 * body and upper_wick < 0.1 * lower_wick and
            body > 0.1 * (high_price - low_price)):
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
        prev_open, prev_close = df['Open'].iloc[i-1], df['Close'].iloc[i-1]
        curr_open, curr_close = df['Open'].iloc[i], df['Close'].iloc[i]
        
        if (prev_close < prev_open and  # Previous day is bearish
            curr_close > curr_open and  # Current day is bullish
            curr_open > prev_close and curr_close < prev_open and  # Current day is inside previous day
            (curr_close - curr_open) < (prev_open - prev_close)):  # Current day body is smaller
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
        prev_open, prev_close = df['Open'].iloc[i-1], df['Close'].iloc[i-1]
        curr_open, curr_close = df['Open'].iloc[i], df['Close'].iloc[i]
        
        mid_point = (prev_open + prev_close) / 2
        
        if (prev_close < prev_open and  # Previous day is bearish
            curr_close > curr_open and  # Current day is bullish
            curr_open < prev_close and  # Open below previous close
            curr_close > mid_point and  # Close above midpoint of previous day
            curr_close < prev_open):  # Close below previous open
            bullish_piercing.append('Bullish Piercing')
        else:
            bullish_piercing.append(np.nan)
    
    return bullish_piercing

def add_candlestick_patterns(df):
    """
    Adds all candlestick patterns to the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame containing the OHLC data.

    Returns:
        pd.DataFrame: DataFrame with added 'Pattern' column containing identified patterns.
    """
    df = df.copy()
    df['Pattern'] = np.nan
    
    patterns = [
        detect_bullish_engulfing(df),
        detect_morning_star(df),
        detect_three_white_soldiers(df),
        detect_hammer(df),
        detect_bullish_harami(df),
        detect_bullish_piercing(df)
    ]
    
    for pattern in patterns:
        df['Pattern'] = df['Pattern'].combine_first(pd.Series(pattern))
    
    return df

def check_bullish_candlestick_pattern(df):
    """
    Checks for bullish candlestick patterns in combination with Ripple status.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Pattern' and 'Ripple_Status' columns.

    Returns:
        pd.DataFrame: DataFrame with added 'Bullish_Candlestick_Pattern' column.
    """
    df['Bullish_Candlestick_Pattern'] = (df['Pattern'].notna()) & (df['Ripple_Status'] == True)
    return df