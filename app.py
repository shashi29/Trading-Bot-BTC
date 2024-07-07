import streamlit as st
import pandas as pd
from config import config
from scanner import StockScanner
from datetime import datetime, time

# Initialize the StockScanner
scanner = StockScanner(config)

def main():
    st.title("Stock Scanner App")

    # Input for stock ticker
    ticker = st.text_input("Enter Stock Ticker:", "AAPL")
    flag_date = st.date_input("Select Date", datetime.now().date())
    flag_time = st.time_input("Select Time", time(12, 30))
    flag_datetime = datetime.combine(flag_date, flag_time)

    if st.button("Scan Stock"):
        with st.spinner("Scanning..."):
            df_Tide, df_Wave, df_Ripple = scanner.Check_buy_condition(ticker)

        # Filter and display only rows where Ripple_Status is True
        buy_signals = df_Ripple[(df_Ripple['Ripple_Status'] == True) & (df_Ripple['Datetime'] >= flag_datetime)]
        
        if not buy_signals.empty:
            st.subheader("Buy Signals (Ripple_Status = True)")
            st.dataframe(buy_signals)
        else:
            st.info("No buy signals detected (No rows with Ripple_Status = True).")

if __name__ == "__main__":
    main()