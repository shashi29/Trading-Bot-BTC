# analysis/tide_analysis.py

import pandas as pd

def analyze_tide(df):
    """
    Perform analysis on the Tide timeframe data.
    
    Args:
    - df (pd.DataFrame): DataFrame containing Tide timeframe data
    
    Returns:
    - dict: Analysis results for the Tide timeframe
    """
    results = {}
    
    # Identify green candles
    results['green_candles'] = df[df['HA_Green'] == True]['Date'].tolist()
    
    # Calculate the percentage of green candles
    results['green_candle_percentage'] = (df['HA_Green'].sum() / len(df)) * 100
    
    # Identify bullish patterns
    results['bullish_patterns'] = df[df['Pattern'].notna()]['Pattern'].value_counts().to_dict()
    
    # Identify the last N (e.g., 5) candles' colors
    n = 5
    results['last_n_candles'] = df['HA_Type'].tail(n).tolist()
    
    # Check if the overall trend is bullish (e.g., more than 60% green candles in the last 20 periods)
    trend_period = 20
    recent_trend = df['HA_Green'].tail(trend_period).mean() > 0.6
    results['recent_bullish_trend'] = recent_trend
    
    return results

def check_tide_condition(df):
    """
    Check if the Tide conditions are favorable for trading.
    
    Args:
    - df (pd.DataFrame): DataFrame containing Tide timeframe data
    
    Returns:
    - bool: True if Tide conditions are favorable, False otherwise
    """
    analysis = analyze_tide(df)
    
    # Define conditions for favorable Tide
    conditions = [
        analysis['green_candle_percentage'] > 50,
        analysis['recent_bullish_trend'],
        len(analysis['bullish_patterns']) > 0
    ]
    
    return all(conditions)