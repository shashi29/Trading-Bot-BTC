import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
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
        if date_column not in df.columns:
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

    def analyze_stock(self, ticker: str, flag_date: datetime.date, period_tide: str, interval_tide: str, period_wave: str, interval_wave: str, period_ripple: str, interval_ripple: str, setting:str="Ripple 15min") -> Tuple[pd.DataFrame, pd.DataFrame]:
        try:
            print(f"Processing {ticker}...")
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
            self.scan_stocks(tickers, flag_date, period_tide, interval_tide, period_wave, interval_wave, period_ripple, interval_ripple, setting)

    def scan_stocks(self, tickers: str, flag_date: datetime.date, period_tide: str, interval_tide: str, period_wave: str, interval_wave: str, period_ripple: str, interval_ripple: str, setting:str="Ripple 15min"):
        tickers_list = [ticker.strip() + ".NS" for ticker in tickers.split(",")]

        for ticker in tickers_list:
            try:
                with st.spinner(f"Scanning {ticker}..."):
                    self.ticker = ticker
                    daily_data, daily_wave = self.analyzer.analyze_stock(ticker, flag_date, period_tide, interval_tide, period_wave, interval_wave, period_ripple, interval_ripple, setting)

                if daily_data['Ripple_Status'].any():
                    self.display_stock_analysis(ticker, flag_date, daily_data, daily_wave, setting)
                else:
                    st.info(f"No buy signals detected for {ticker} on {flag_date}.")
            except Exception as e:
                logger.error(f"Error analyzing stock {ticker} : {str(e)}", exc_info=True)
                
        # Display the overall summary
        buy_summary = pd.DataFrame(self.buy_summary)
        st.subheader("Overall Profit with Strategy")
        st.dataframe(buy_summary, use_container_width=True)

    def display_stock_analysis(self, ticker: str, flag_date: datetime.date, daily_data: pd.DataFrame, daily_wave: pd.DataFrame, setting:str="Ripple 15min"):
        st.subheader(f"Results for {ticker} on {flag_date}")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Candlestick Chart", "Ripple Data", "Wave Data" ,"Wave Sell Strategy", "Ripple Sell Strategy", "EMA Sell Strategy"])

        with tab1:
            st.subheader(f"Ripple Data")
            fig = ChartPlotter.plot_candlestick(daily_data)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader(f"Wave Data")
            fig = ChartPlotter.plot_candlestick(daily_wave)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.dataframe(daily_data, use_container_width=True)
            
        with tab3:
            st.dataframe(daily_wave, use_container_width=True)

        with tab4:
            if setting == "Ripple 15min":
                strategy = WaveSellStrategy()
            else:
                strategy = WaveSellStrategyRipple1hr()
            self.display_strategy_results(strategy, daily_data, daily_wave, "Wave Sell Strategy")

        with tab5:
            if setting == "Ripple 15min":
                strategy = RippleSellStrategy()
            else:
                strategy = RippleSellStrategyRipple1hr()
            self.display_strategy_results(strategy, daily_data, daily_wave, "Ripple Sell Strategy")
        
        with tab6:
            if setting == "Ripple 15min":
                strategy = EMACrossStrategy()
            else:
                strategy = EMACrossStrategyRipple1hr()
            self.display_strategy_results(strategy, daily_data, daily_wave, "EMA Sell Strategy")

    def display_strategy_results(self, strategy: TradingStrategy, daily_data: pd.DataFrame, daily_wave: pd.DataFrame, strategy_name: str):
        trade_log, win_ratio, profit_percentage = strategy.execute(daily_data, daily_wave)
        self.buy_summary.append({
            "Ticker": self.ticker,
            "Sell Strategy": strategy_name,
            "Win Ratio": win_ratio,
            "Profit Percentage": profit_percentage
        })
        st.subheader(f"Trade Log - {strategy_name}")
        st.dataframe(trade_log, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Win Ratio", f"{win_ratio}%")
        col2.metric("Profit Percentage", f"{profit_percentage}%")

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
