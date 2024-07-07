import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time
from config import config
from scanner import StockScanner

# Initialize the StockScanner
scanner = StockScanner(config)

def plot_candlestick(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df['Datetime'],
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
        template="plotly_white"
    )
    
    return fig

def main():
    st.title("Stock Scanner App")

    # Input for stock ticker
    ticker = st.text_input("Enter Stock Ticker:", "DIXON.NS")
    flag_date = st.date_input("Select Date", datetime.now().date())
    flag_time = st.time_input("Select Time", time(12, 30))
    flag_datetime = datetime.combine(flag_date, flag_time)

    if st.button("Scan Stock"):
        with st.spinner("Scanning..."):
            df_Tide, df_Wave, df_Ripple = scanner.Check_buy_condition(ticker)

        # Filter and display only rows where Ripple_Status is True
        buy_signals = df_Ripple[(df_Ripple['Ripple_Status'] == True) & (df_Ripple['Datetime'] >= flag_datetime)]
        buy_signals = buy_signals[['Datetime', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close', 'Volume', 'HA_Type', 'HA_Green', 'HA_Red', 'Pattern', 'Price_Above_EMA', 'RSI_Type', 'ADX_14', 'ADX Status', 'Stochastic_PCO', 'Stochastic_Oversold', 'Stochastic_PC_from_Oversold', 'Below_618']]

        if not buy_signals.empty:
            st.subheader("Buy Signals (Ripple_Status = True)")
            st.dataframe(buy_signals)
            
            # Plot candlestick chart
            fig = plot_candlestick(buy_signals)
            st.plotly_chart(fig)
        else:
            st.info("No buy signals detected (No rows with Ripple_Status = True).")

if __name__ == "__main__":
    main()
