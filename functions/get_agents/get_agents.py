import pandas as pd
from datetime import datetime
import requests

def get_agents(df):
  df_agents = df[df['roles'].str.contains('ROLE_AGENT')][['id', 'username']]
  df_agents.rename(columns={'id': 'user_id'}, inplace=True)
  return df_agents
