import pandas as pd
import numpy as np

# Function to calculate Fibonacci retracement levels
def calculate_fib_levels(high, low):
    fib_levels = {
        0.236: high - (0.236 * (high - low)),
        0.382: high - (0.382 * (high - low)),
        0.5: high - (0.5 * (high - low)),
        0.618: high - (0.618 * (high - low)),
        # Add more Fibonacci levels as needed
    }
    return fib_levels

# Function to determine if current price is below 61.8% Fibonacci retracement level
def predict_below_618(df):
    df['Below_618'] = False  # Initialize new column
    
    for index, row in df.iterrows():
        current_price = row['Close']
        
        # Calculate high and low of last wave (example using last 30 days)
        if index >= 30:
            last_wave_high = df.loc[index-30:index-1, 'Close'].max()
            last_wave_low = df.loc[index-30:index-1, 'Close'].min()
            
            # Calculate Fibonacci levels for the last wave
            fib_levels = calculate_fib_levels(last_wave_high, last_wave_low)
            
            # Check if current price is below 61.8% retracement level of last wave
            fib_618 = fib_levels[0.618]
            below_618 = current_price < fib_618
            
            # Update 'Below_618' column in DataFrame
            df.at[index, 'Below_618'] = below_618
    
    return df