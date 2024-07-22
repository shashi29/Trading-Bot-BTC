import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        pass


class WaveSellStrategyRipple1hr(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

        for index, row in df.iterrows():
            wave = df_wave[(df_wave['Datetime'].dt.date == row['Datetime'].date()) & (df_wave['HA_Type'] == "Solid Red")]

            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
            elif len(wave) and position > 0:
                sell_price = row['Close']
                capital = position * sell_price
                position = 0
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                trade_log[-1].update({
                    'Sell Time': row['Datetime'],
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss
                })

        # Check for any open trades on the last day
        # if position > 0:
        #     last_row = df.iloc[-1]
        #     sell_price = last_row['Close']
        #     capital = position * sell_price
        #     profit_loss = sell_price - buy_price
        #     profit_percentage = (profit_loss / buy_price) * 100
        #     win_loss = 'Win' if profit_loss > 0 else 'Loss'
        #     trade_log[-1].update({
        #         'Sell Time': last_row['Datetime'],
        #         'Sell Price': sell_price,
        #         'Profit/Loss': profit_loss,
        #         'Profit Percentage': profit_percentage,
        #         'Win/Loss': win_loss
        #     })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0
        # Calculate the average profit percentage
        profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
        average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

        return pd.DataFrame(trade_log), win_ratio, average_profit_percentage        

class RippleSellStrategyRipple1hr(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        try:
            # Convert 'Datetime' to datetime objects
            df['Datetime'] = pd.to_datetime(df['Datetime'])

            for index, row in df.iterrows():
                # Check for buy condition
                if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                    position = capital / row['Close']
                    buy_price = row['Close']
                    capital = 0
                    trade_log.append({
                        'Buy Time': row['Datetime'],
                        'Buy Price': buy_price,
                        'Win/Loss': ''  # Initialize 'Win/Loss' key
                    })

                # Check for sell conditions
                elif (not row['Ripple_Status'] or row['HA_Type'] == 'Solid Red') and position > 0:
                    sell_price = row['Close']
                    capital = position * sell_price
                    position = 0
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    trade_log[-1].update({
                        'Sell Time': row['Datetime'],
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss
                    })

            # Check for any open trades on the last day
            # if position > 0:
            #     last_row = df.iloc[-1]
            #     sell_price = last_row['Close']
            #     capital = position * sell_price
            #     profit_loss = sell_price - buy_price
            #     profit_percentage = (profit_loss / buy_price) * 100
            #     win_loss = 'Win' if profit_loss > 0 else 'Loss'
            #     trade_log[-1].update({
            #         'Sell Time': last_row['Datetime'],
            #         'Sell Price': sell_price,
            #         'Profit/Loss': profit_loss,
            #         'Profit Percentage': profit_percentage,
            #         'Win/Loss': win_loss
            #     })

            # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
            for trade in trade_log:
                if 'Win/Loss' not in trade:
                    trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

            

            num_trades = len(trade_log)
            wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

            win_ratio = wins / num_trades if num_trades > 0 else 0
            # Calculate the average profit percentage
            profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
            average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

            return pd.DataFrame(trade_log), win_ratio, average_profit_percentage  

        except Exception as ex:
            print(f"An error occurred during trading: {str(ex)}")
            return pd.DataFrame(trade_log), 0, 0


class EMACrossStrategyRipple1hr(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])

        # Calculate 5-hour and 13-hour EMA
        df['5EMA'] = df['Close'].ewm(span=5, adjust=False).mean()
        df['13EMA'] = df['Close'].ewm(span=13, adjust=False).mean()

        for index, row in df.iterrows():
            # Check for buy condition
            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    '5EMA': row['5EMA'],
                    '13EMA': row['13EMA'],
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
                        
            # Check for EMA crossover to trigger sell
            elif position > 0:
                if row['5EMA'] < row['13EMA']:  # 5EMA crosses below 13EMA
                    sell_price = row['Close']
                    sell_time = row['Datetime']
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    capital = position * sell_price
                    position = 0
                    trade_log[-1].update({
                        'Sell Time': sell_time,
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss,
                        '5EMA': row['5EMA'],
                        '13EMA': row['13EMA']
                    })

        # Check for any open trades on the last day
        # if position > 0:
        #     last_row = df.iloc[-1]
        #     sell_price = last_row['Close']
        #     capital = position * sell_price
        #     profit_loss = sell_price - buy_price
        #     profit_percentage = (profit_loss / buy_price) * 100
        #     win_loss = 'Win' if profit_loss > 0 else 'Loss'
        #     trade_log[-1].update({
        #         'Sell Time': last_row['Datetime'],
        #         'Sell Price': sell_price,
        #         'Profit/Loss': profit_loss,
        #         'Profit Percentage': profit_percentage,
        #         'Win/Loss': win_loss
        #     })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0
        
        # Calculate the average profit percentage
        profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
        average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

        return pd.DataFrame(trade_log), win_ratio, average_profit_percentage


#15 min Ripple Strategy
class WaveSellStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

        for index, row in df.iterrows():
            wave = df_wave[(df_wave['Datetime'] == row['Datetime']) & (df_wave['HA_Type'] == "Solid Red")]

            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
            elif len(wave) and position > 0:
                sell_price = row['Close']
                capital = position * sell_price
                position = 0
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                trade_log[-1].update({
                    'Sell Time': row['Datetime'],
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss
                })

            # Check if it's the last time frame of the day and we have an open position
            if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                sell_price = row['Close']
                sell_time = row['Datetime']
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                capital = position * sell_price
                position = 0
                trade_log[-1].update({
                    'Sell Time': sell_time,
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss
                })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0

        # Calculate the average profit percentage
        profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
        average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

        return pd.DataFrame(trade_log), win_ratio, average_profit_percentage  

class RippleSellStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        try:
            # Convert 'Datetime' to datetime objects
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

            for index, row in df.iterrows():
                # Check for buy condition
                if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                    position = capital / row['Close']
                    buy_price = row['Close']
                    capital = 0
                    trade_log.append({
                        'Buy Time': row['Datetime'],
                        'Buy Price': buy_price,
                        'Win/Loss': ''  # Initialize 'Win/Loss' key
                    })
                
                # Check for sell conditions
                elif (not row['Ripple_Status'] or row['HA_Type'] == 'Solid Red') and position > 0:
                    sell_price = row['Close']
                    capital = position * sell_price
                    position = 0
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    trade_log[-1].update({
                        'Sell Time': row['Datetime'],
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss
                    })

                # Check for end-of-day sell logic (3:15 PM)
                if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                    sell_price = row['Close']
                    sell_time = row['Datetime']
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    capital = position * sell_price
                    position = 0
                    trade_log[-1].update({
                        'Sell Time': sell_time,
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss
                    })

            # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
            for trade in trade_log:
                if 'Win/Loss' not in trade:
                    trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

            

            num_trades = len(trade_log)
            wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

            win_ratio = wins / num_trades if num_trades > 0 else 0
            # Calculate the average profit percentage
            profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
            average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

            return pd.DataFrame(trade_log), win_ratio, average_profit_percentage  

        except Exception as ex:
            print(f"An error occurred during trading: {str(ex)}")
            return pd.DataFrame(trade_log), 0, 0

class EMACrossStrategy(TradingStrategy):
    def execute(self, df: pd.DataFrame, df_wave: pd.DataFrame) -> Tuple[pd.DataFrame, float, float]:
        initial_capital = 100000000000
        capital = initial_capital
        position = 0
        buy_price = 0
        trade_log = []

        # Convert 'Datetime' to datetime objects
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df_wave['Datetime'] = pd.to_datetime(df_wave['Datetime'])

        # Calculate 5-day and 13-day EMA
        df['5EMA'] = df['Close'].ewm(span=5, adjust=False).mean()
        df['13EMA'] = df['Close'].ewm(span=13, adjust=False).mean()

        for index, row in df.iterrows():
            #wave = df_wave[(df_wave['Datetime'] == row['Datetime']) & (df_wave['HA_Type'] == "Solid Red")]

            if row['Ripple_Status'] and row['HA_Type'] == 'Solid Green' and position == 0:
                position = capital / row['Close']
                buy_price = row['Close']
                capital = 0
                trade_log.append({
                    'Buy Time': row['Datetime'],
                    'Buy Price': buy_price,
                    '5EMA': row['5EMA'],
                    '13EMA': row['13EMA'],
                    'Win/Loss': ''  # Initialize 'Win/Loss' key
                })
                        
            # Check for EMA crossover to trigger sell
            elif position > 0:
                if row['5EMA'] < row['13EMA']:  # 5EMA crosses below 13EMA
                    sell_price = row['Close']
                    sell_time = row['Datetime']
                    profit_loss = sell_price - buy_price
                    profit_percentage = (profit_loss / buy_price) * 100
                    win_loss = 'Win' if profit_loss > 0 else 'Loss'
                    capital = position * sell_price
                    position = 0
                    trade_log[-1].update({
                        'Sell Time': sell_time,
                        'Sell Price': sell_price,
                        'Profit/Loss': profit_loss,
                        'Profit Percentage': profit_percentage,
                        'Win/Loss': win_loss,
                        '5EMA': row['5EMA'],
                        '13EMA': row['13EMA']
                    })

            # Check if it's the last time frame of the day and we have an open position
            if row['Datetime'].time() == pd.Timestamp('15:15:00').time() and position > 0:
                sell_price = row['Close']
                sell_time = row['Datetime']
                profit_loss = sell_price - buy_price
                profit_percentage = (profit_loss / buy_price) * 100
                win_loss = 'Win' if profit_loss > 0 else 'Loss'
                capital = position * sell_price
                position = 0
                trade_log[-1].update({
                    'Sell Time': sell_time,
                    'Sell Price': sell_price,
                    'Profit/Loss': profit_loss,
                    'Profit Percentage': profit_percentage,
                    'Win/Loss': win_loss,
                    '5EMA': row['5EMA'],
                    '13EMA': row['13EMA']
                })

        # After exiting the loop, ensure all entries in trade_log have 'Win/Loss' key
        for trade in trade_log:
            if 'Win/Loss' not in trade:
                trade['Win/Loss'] = ''  # Handle cases where 'Win/Loss' key was not updated

        

        num_trades = len(trade_log)
        wins = sum(1 for trade in trade_log if trade['Win/Loss'] == 'Win')

        win_ratio = wins / num_trades if num_trades > 0 else 0
        
        # Calculate the average profit percentage
        profit_percentages = [trade['Profit Percentage'] for trade in trade_log if 'Profit Percentage' in trade]
        average_profit_percentage = sum(profit_percentages) if profit_percentages else 0

        return pd.DataFrame(trade_log), win_ratio, average_profit_percentage  