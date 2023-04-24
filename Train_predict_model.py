# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from autots import AutoTS
import plotly.graph_objects as go
# Create a Plotly figure object
import plotly.express as px

def train_predict(df, forecast_length):
    #df['DATE'] = pd.to_datetime(df['DATE'])
    #store_data = df.set_index('DATE')
    store_data = df
    model = AutoTS(
        forecast_length=forecast_length,
        frequency='infer',
        prediction_interval=0.9,
        #ensemble=None,
        model_list="superfast",  # "superfast", "default", "fast_parallel"
        transformer_list="superfast",  # "superfast",
        drop_most_recent=1,
        max_generations=4,
        num_validations=2,
        validation_method="backwards"
    )

    model.fit(store_data['Open'])
    prediction = model.predict()
    # point forecasts dataframe
    forecasts_df = prediction.forecast
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=store_data.index, y=store_data['Open'],
                    mode='lines+markers',
                    name='Train'))
    fig.add_trace(go.Scatter(x=forecasts_df.index, y=forecasts_df['Open'],
                        mode='lines+markers',
                        name='Predict'))
    fig.show()

df = pd.read_csv("/workspaces/Trading-Bot-BTC/data/BTC-USD.csv")

train_predict(df, 14)