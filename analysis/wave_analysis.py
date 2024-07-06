# analysis/wave_analysis.py

import pandas as pd

def analyze_wave(df):
    """
    Perform analysis on the Wave timeframe data.
    
    Args:
    - df (pd.DataFrame): DataFrame containing Wave timeframe data
    
    Returns:
    - dict: Analysis results for the Wave timeframe
    """
    results = {}
    
    # Analyze EMA
    results['above_ema'] = (df['Close'] > df['EMA']).sum() / len(df) * 100
    results['ema_slope_positive'] = (df['EMA_Slope'] > 0).sum() / len(df) * 100
    
    # Analyze Heikin Ashi candles
    results['green_candles'] = df[df['HA_Green'] == True]['Datetime'].tolist()
    results['green_candle_percentage'] = (df['HA_Green'].sum() / len(df)) * 100
    
    # Analyze recent trend
    n = 12  # Last 12 hours for hourly data
    recent_df = df.tail(n)
    results['recent_above_ema'] = (recent_df['Close'] > recent_df['EMA']).sum() / n * 100
    results['recent_ema_slope_positive'] = (recent_df['EMA_Slope'] > 0).sum() / n * 100
    results['recent_green_candle_percentage'] = (recent_df['HA_Green'].sum() / n) * 100
    
    return results

def check_wave_condition(df, tide_condition):
    """
    Check if the Wave conditions are favorable for trading.
    
    Args:
    - df (pd.DataFrame): DataFrame containing Wave timeframe data
    - tide_condition (bool): Whether the Tide condition is favorable
    
    Returns:
    - bool: True if Wave conditions are favorable, False otherwise
    """
    if not tide_condition:
        return False
    
    analysis = analyze_wave(df)
    
    # Define conditions for favorable Wave
    conditions = [
        analysis['above_ema'] > 50,
        analysis['ema_slope_positive'] > 50,
        analysis['green_candle_percentage'] > 50,
        analysis['recent_above_ema'] > 60,
        analysis['recent_ema_slope_positive'] > 60,
        analysis['recent_green_candle_percentage'] > 60
    ]
    
    return all(conditions)