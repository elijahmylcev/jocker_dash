import pandas as pd
from datetime import datetime
import requests
from functions import get_df_from_table

def get_rating_table(
  table_deals_name,
  engine
):
  # Deals
  df_deals = get_df_from_table(table_deals_name, engine)
  df_deals['complete_date'] = pd.to_datetime(df_deals['complete_date'])

  df_deals_in_progress = df_deals[(df_deals['complete_date'].isnull()) & (df_deals['deleted'] == 0)
                    & (df_deals['status'] != 6)]
  df_deals_in_progress = df_deals_in_progress.groupby('user_id').size().reset_index(name='progress')
  df_deals_in_success_all_time = df_deals[df_deals['status'] == 6]
  df_deals_in_success_all_time = df_deals_in_success_all_time.groupby('user_id').size().reset_index(name='compleat')
  result = pd.merge(df_deals_in_progress, df_deals_in_success_all_time, on='user_id')
  result = result.assign(convers=round((result["progress"] + result["compleat"]) / result["compleat"], 2))
  
  