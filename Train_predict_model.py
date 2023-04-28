import pandas as pd
import finrl
from finrl.model import DRLAgent
from finrl.env.env_stocktrading import StockTradingEnv

# Load the data
df = pd.read_csv('/workspaces/Trading-Bot-BTC/daily_data/BTC-USD.csv')

# Split the data into training and testing sets
train_data = df.iloc[:int(len(df)*0.9)]
test_data = df.iloc[int(len(df)*0.9):]

# Define the trading environment using the training data
train_env = finrl.make_env(
    env_id='StockTradingEnv-v1',
    df=train_data,
    mode='train'
)

# Train an RL algorithm using the training environment
agent = DRLAgent(env=train_env)
model = agent.get_model(model_name='ddpg')
trained_model = agent.train_model(model=model, 
                                  tb_log_name='ddpg',
                                  total_timesteps=50000)

# Define the trading environment using the testing data
test_env = finrl.make_env(
    env_id='StockTradingEnv-v1',
    df=test_data,
    mode='test'
)

# Evaluate the performance of the trained RL algorithm on the testing environment
df_account_value, df_actions = DRLAgent.evaluate_model(
    model=trained_model, 
    environment=test_env, 
    num_steps=len(test_data), 
    verbose=True
)
