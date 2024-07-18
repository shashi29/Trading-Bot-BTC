import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
from typing import Tuple
from config import config
from scanner import StockScanner
from trading_strategy.sell_strategy import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chart plotter
class ChartPlotter:
    @staticmethod
    def plot_candlestick(df: pd.DataFrame) -> go.Figure:
        date_column = "Datetime"
        if (date_column not in df.columns) or (df[date_column].isnull().all()):
            date_column = "Date"
        fig = go.Figure(data=[go.Candlestick(
            x=df[date_column],
            open=df['HA_Open'],
            high=df['HA_High'],
            low=df['HA_Low'],
            close=df['HA_Close'],
            name='Candlesticks'
        )])
        
        fig.update_layout(
            title="Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            xaxis_type='category'
        )
        
        return fig

# Stock analyzer
class StockAnalyzer:
    def __init__(self, scanner: StockScanner):
        self.scanner = scanner

    def analyze_stock(self, ticker: str, flag_date: datetime.date, period_tide: str, interval_tide: str, period_wave: str, interval_wave: str, period_ripple: str, interval_ripple: str, setting:str="Ripple 15min", strategies:list=["Wave", "Ripple", "EMA"]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            logger.info(f"Processing {ticker}...")
            df_Tide = self.scanner.process_tide_data(ticker, period=period_tide, interval=interval_tide)
            df_Wave = self.scanner.process_wave_data(ticker, period=period_wave, interval=interval_wave)
            df_Ripple = self.scanner.process_ripple_data(ticker, period=period_ripple, interval=interval_ripple)
            if setting == "Ripple 15min":
                df_Tide, df_Wave, df_Ripple = self.scanner.Check_buy_condition(ticker, df_Tide, df_Wave, df_Ripple)
                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_ripple = df_Ripple[df_Ripple['Date'] >= flag_date]
                df_Wave['Date'] = df_Wave['Datetime'].dt.date
                daily_wave = df_Wave[df_Wave['Date'] >= flag_date]
            else:
                df_Tide, df_Wave, df_Ripple = self.scanner.Check_buy_condition_ripple_1hr(ticker, df_Tide, df_Wave, df_Ripple)
                df_Ripple['Date'] = df_Ripple['Datetime'].dt.date
                daily_ripple = df_Ripple[df_Ripple['Date'] >= flag_date]
                flag_date = pd.to_datetime(flag_date)
                daily_wave = df_Wave[df_Wave['Date'] >= flag_date]
                logger.info(f"Shape of Wave data {daily_wave.shape} and Ripple Data {daily_ripple.shape}")
            return daily_ripple, daily_wave
        except Exception as e:
            logger.error(f"Error analyzing stock {ticker} : {str(e)}", exc_info=True)
            raise

# Streamlit UI
class StockScannerApp:
    def __init__(self, analyzer: StockAnalyzer):
        self.analyzer = analyzer
        self.buy_summary = list()
        self.ticker = ''
        self.refresh_key = "refresh_key"

    def run(self):
        st.set_page_config(page_title="Stock Scanner App", layout="wide")
        st.title("Stock Scanner App")

        col1, col2 = st.columns(2)
        with col1:
            tickers = st.text_area("Enter Stock Tickers (comma-separated):", "RELIANCE, INFY")
        with col2:
            flag_date = st.date_input("Select Date", datetime.now().date())

        st.sidebar.header("Yahoo Finance Settings")
        with st.sidebar:
            setting = st.radio("Select Setting:", ["Ripple 15min", "Ripple 1h"])
            strategies = st.multiselect("Select Strategies:", ["Wave", "Ripple", "EMA"], default=["Wave", "Ripple", "EMA"])

        if setting == "Ripple 15min":
            period_tide = "1mo"
            interval_tide = "1d"
            period_wave = "1mo"
            interval_wave = "1h"
            period_ripple = "1mo"
            interval_ripple = "15m"
        else:  # Ripple 1h
            period_tide = "3mo"
            interval_tide = "1wk"
            period_wave = "3mo"
            interval_wave = "1d"
            period_ripple = "3mo"
            interval_ripple = "1h"

        if st.button("Scan Stocks", key="scan_button"):
            tickers_list = [ticker.strip() + ".NS" for ticker in tickers.split(",")]
            results_placeholder = st.empty()

            for ticker in tickers_list:
                try:
                    with st.spinner(f"Scanning {ticker}..."):
                        self.ticker = ticker
                        daily_data, daily_wave = self.analyzer.analyze_stock(ticker, flag_date, period_tide, interval_tide, period_wave, interval_wave, period_ripple, interval_ripple, setting, strategies)

                    if daily_data['Ripple_Status'].any():
                        self.collect_summary(ticker, flag_date, daily_data, daily_wave, setting, strategies)
                    else:
                        logger.info(f"No buy signals detected for {ticker} on {flag_date}.")
                    
                    # Update results in placeholder
                    results_placeholder.write(f"Processed {ticker} successfully.")
                except Exception as e:
                    logger.error(f"Error analyzing stock {ticker} : {str(e)}", exc_info=True)
                    results_placeholder.write(f"Error processing {ticker}. Check logs for details.")

            # Display the overall summary
            buy_summary = pd.DataFrame(self.buy_summary)
            st.subheader("Overall Profit with Strategy")
            st.dataframe(buy_summary, use_container_width=True)

    def collect_summary(self, ticker: str, flag_date: datetime.date, daily_data: pd.DataFrame, daily_wave: pd.DataFrame, setting:str="Ripple 15min", strategies:list=["Wave", "Ripple", "EMA"]):
        summary_data = []

        if setting == "Ripple 15min":
            if "Wave" in strategies:
                wave_strategy = WaveSellStrategy()
                wave_trade_log, wave_win_ratio, wave_profit_percentage = wave_strategy.execute(daily_data, daily_wave)
                if not wave_trade_log.empty:
                    summary_data.append({
                        "Ticker": ticker,
                        "Sell Strategy": "Wave",
                        "Buy Time": wave_trade_log['Buy Time'].iloc[-1],
                        "Buy Price": wave_trade_log['Buy Price'].iloc[-1],
                        "Sell Time": wave_trade_log['Sell Time'].iloc[-1],
                        "Sell Price": wave_trade_log['Sell Price'].iloc[-1],
                        "Profit/Loss Percentage": wave_trade_log['Profit Percentage'].iloc[-1]
                    })
            if "Ripple" in strategies:
                ripple_strategy = RippleSellStrategy()
                ripple_trade_log, ripple_win_ratio, ripple_profit_percentage = ripple_strategy.execute(daily_data, daily_wave)
                if not ripple_trade_log.empty:
                    summary_data.append({
                        "Ticker": ticker,
                        "Sell Strategy": "Ripple",
                        "Buy Time": ripple_trade_log['Buy Time'].iloc[-1],
                        "Buy Price": ripple_trade_log['Buy Price'].iloc[-1],
                        "Sell Time": ripple_trade_log['Sell Time'].iloc[-1],
                        "Sell Price": ripple_trade_log['Sell Price'].iloc[-1],
                        "Profit/Loss Percentage": ripple_trade_log['Profit Percentage'].iloc[-1]
                    })
            if "EMA" in strategies:
                ema_strategy = EMACrossStrategy()
                ema_trade_log, ema_win_ratio, ema_profit_percentage = ema_strategy.execute(daily_data, daily_wave)
                if not ema_trade_log.empty:
                    summary_data.append({
                        "Ticker": ticker,
                        "Sell Strategy": "EMA",
                        "Buy Time": ema_trade_log['Buy Time'].iloc[-1],
                        "Buy Price": ema_trade_log['Buy Price'].iloc[-1],
                        "Sell Time": ema_trade_log['Sell Time'].iloc[-1],
                        "Sell Price": ema_trade_log['Sell Price'].iloc[-1],
                        "Profit/Loss Percentage": ema_trade_log['Profit Percentage'].iloc[-1]
                    })

        self.buy_summary.extend(summary_data)

def main():
    try:
        scanner = StockScanner(config)
        analyzer = StockAnalyzer(scanner)
        app = StockScannerApp(analyzer)
        app.run()
    except Exception as e:
        logger.error(f"An error occurred in the main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()
