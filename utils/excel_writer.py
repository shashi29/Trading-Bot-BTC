import pandas as pd

class ExcelWriter:

    @staticmethod
    def generate_column_explanations():
        explanations = {
            'Tide': {
                'Date': 'Date of the trading day',
                'Open': 'Opening price of the stock',
                'High': 'Highest price of the stock during the day',
                'Low': 'Lowest price of the stock during the day',
                'Close': 'Closing price of the stock',
                'Adj Close': 'Adjusted closing price',
                'Volume': 'Number of shares traded',
                'HA_Close': 'Heikin Ashi Close price',
                'HA_Open': 'Heikin Ashi Open price',
                'HA_High': 'Heikin Ashi High price',
                'HA_Low': 'Heikin Ashi Low price',
                'HA_Type': 'Type of Heikin Ashi candle',
                'HA_Green': 'Boolean indicating if the Heikin Ashi candle is green',
                'Pattern': 'Detected candlestick pattern'
            },
            'Wave': {
                'Datetime': 'Date and time of the trading hour',
                'Open': 'Opening price of the stock',
                'High': 'Highest price of the stock during the hour',
                'Low': 'Lowest price of the stock during the hour',
                'Close': 'Closing price of the stock',
                'Adj Close': 'Adjusted closing price',
                'Volume': 'Number of shares traded',
                'HA_Close': 'Heikin Ashi Close price',
                'HA_Open': 'Heikin Ashi Open price',
                'HA_High': 'Heikin Ashi High price',
                'HA_Low': 'Heikin Ashi Low price',
                'HA_Type': 'Type of Heikin Ashi candle',
                'HA_Green': 'Boolean indicating if the Heikin Ashi candle is green',
                'Pattern': 'Detected candlestick pattern',
                'EMA': 'Exponential Moving Average',
                'EMA_Slope': 'Slope of the EMA',
                'EMA_Slope_Up': 'Boolean indicating if EMA slope is positive',
                'Wave_Status': 'Boolean indicating Wave status'
            },
            'Ripple': {
                'Datetime': 'Date and time of the 15-minute interval',
                'Open': 'Opening price of the stock',
                'High': 'Highest price of the stock during the interval',
                'Low': 'Lowest price of the stock during the interval',
                'Close': 'Closing price of the stock',
                'Adj Close': 'Adjusted closing price',
                'Volume': 'Number of shares traded',
                'HA_Close': 'Heikin Ashi Close price',
                'HA_Open': 'Heikin Ashi Open price',
                'HA_High': 'Heikin Ashi High price',
                'HA_Low': 'Heikin Ashi Low price',
                'HA_Type': 'Type of Heikin Ashi candle',
                'HA_Green': 'Boolean indicating if the Heikin Ashi candle is green',
                'Pattern': 'Detected candlestick pattern',
                'EMA_50': '50-period Exponential Moving Average',
                'Price_Above_EMA': 'Boolean indicating if price is above EMA',
                'FBD_Signal': 'Fake Break Down signal',
                'Ripple_Status': 'Boolean indicating Ripple status',
                'SMA': 'Simple Moving Average for Bollinger Bands',
                'SD': 'Standard Deviation for Bollinger Bands',
                'UBB': 'Upper Bollinger Band',
                'LBB': 'Lower Bollinger Band',
                'Bollinger_Band_Condition': 'Boolean indicating Bollinger Band condition',
                'Bullish_Candlestick_Pattern': 'Boolean indicating bullish candlestick pattern',
                'RSI': 'Relative Strength Index',
                'RSI_Type': 'Classification of RSI value',
                'RSI_Flag': 'Boolean indicating RSI condition',
                'TR': 'True Range for DMI',
                '+DM': 'Positive Directional Movement',
                '-DM': 'Negative Directional Movement',
                '+DI': 'Positive Directional Indicator',
                '-DI': 'Negative Directional Indicator',
                'ADX': 'Average Directional Index',
                'ADX_Uptick': 'Boolean indicating if ADX is increasing',
                'ADX_Good': 'Classification of ADX value',
                'ADX_Forming_Ungli': 'Boolean indicating ADX forming condition',
                '%K': 'Stochastic Oscillator %K line',
                '%D': 'Stochastic Oscillator %D line',
                'Stochastic_PCO': 'Boolean indicating Stochastic Positive Crossover',
                'Stochastic_Oversold': 'Boolean indicating Stochastic Oversold condition',
                'Stochastic_PC_from_Oversold': 'Boolean indicating Stochastic Positive Crossover from Oversold'
            }
        }
        return explanations
    
    @staticmethod
    def write(ticker, data): 
        # Save all DataFrames to one Excel sheet
        df_Tide, df_Wave, df_Ripple = data['Tide'], data['Wave'], data['Ripple']
        explanations = ExcelWriter.generate_column_explanations()

        with pd.ExcelWriter(f'report/{ticker}_report.xlsx') as writer:
            df_Tide.to_excel(writer, sheet_name='Tide', index=False)
            df_Wave.to_excel(writer, sheet_name='Wave', index=False)
            df_Ripple.to_excel(writer, sheet_name='Ripple', index=False)        
            
            # Create the explanatory sheet
            explanation_data = []
            for sheet, columns in explanations.items():
                for column, explanation in columns.items():
                    explanation_data.append([sheet, column, explanation])
            
            df_explanations = pd.DataFrame(explanation_data, columns=['Sheet', 'Column', 'Explanation'])
            df_explanations.to_excel(writer, sheet_name='Column Explanations', index=False)