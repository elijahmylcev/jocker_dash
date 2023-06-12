import pandas as pd
from datetime import datetime
import requests
from functions import get_df_from_table,get_agents
from config import API_TOKEN, URL_API

def get_rating_table(engine, start, end, now):
  # Leads
  payload = {"token": API_TOKEN}
  response = requests.get(URL_API, params=payload)
  df_leads_api = pd.DataFrame(response.json()['data'])
  df_leads_api.dropna(subset=['source'], inplace=True)
  df_leads_api.dropna(subset=['date_update'], inplace=True)
  df_leads_api['date_update'] = df_leads_api['date_update'].apply(lambda x: x['date'])
  df_leads_api['date_update'] = pd.to_datetime(df_leads_api['date_update'])
  df_leads_api['date_update'] = df_leads_api['date_update'].dt.date
  df_leads_api = df_leads_api[(df_leads_api['date_update'] >= start.date()) 
                              & (df_leads_api['date_update'] <= end.date())]

  df_leads_api.rename(columns={'manager_id': 'user_id'}, inplace=True)
  person_recom = df_leads_api[(df_leads_api['source'].str.contains('личная рекомендация')) | 
                              (df_leads_api['source_id'] == 57)]
  # Рекомендации за промежуток времени
  person_recom = person_recom.groupby('user_id').size().reset_index(name='recom')
  # Deals
  df_deals = get_df_from_table('deals', engine)
  df_deals['complete_date'] = pd.to_datetime(df_deals['complete_date'])

  df_deals_in_progress = df_deals[(df_deals['complete_date'].isnull()) & (df_deals['deleted'] == 0)
                    & (df_deals['status'] != 6)]
  df_deals_in_progress = df_deals_in_progress.groupby('user_id').size().reset_index(name='progress')
  df_deals_in_success_all_time = df_deals[df_deals['status'] == 6]
  df_deals_in_success_all_time = df_deals_in_success_all_time.groupby('user_id').size().reset_index(name='compleat')
  df_deals_in_success_all_time #10
  result_prs = df_deals_in_progress.merge(df_deals_in_success_all_time, how='outer', on='user_id')
  result_prs = result_prs.assign(convers=round((result_prs["progress"] + result_prs["compleat"]) / result_prs["compleat"], 2))

  # Успешные сделки за указанный год и месяц
  df_deals_success = df_deals[df_deals['complete'] == 1]
  df_deals_success = df_deals_success[(df_deals_success['status'] == 6) &
                                      (df_deals_success['complete_date'] >= start) &
                                      (df_deals_success['complete_date'] <= end)]
  success = df_deals_success.groupby('user_id').size().reset_index(name='success')
  df_agents = get_agents('fos_user', engine)
  result = df_agents.merge(success, how='outer', on='user_id')
  result = result.merge(person_recom, how='outer', on='user_id')
  result = result.merge(result_prs, how='outer', on='user_id')
  result = result.fillna(0)
  result_deals = result[['user_id', 'username', 'success', 'recom', 'convers']]
  
  # Tasks
  df_tasks_all_time = get_df_from_table('tasks', engine)
  df_tasks_all_time['complete_date'] = pd.to_datetime(df_tasks_all_time['complete_date'])
  df_tasks_all_time['end'] = pd.to_datetime(df_tasks_all_time['end'])
  df_tasks_all_time['start'] = pd.to_datetime(df_tasks_all_time['start'])
  # Исхожу из предположения, что worker_id - исполнитель

  # Условие - дата старта задачи в интервале или дата завершения в интервале
  df_tasks_interval = df_tasks_all_time[((df_tasks_all_time['start'] >= start) 
                                          & (df_tasks_all_time['start'] <= end)) 
                                          | ((df_tasks_all_time['complete_date'] >= start)
                                          & (df_tasks_all_time['complete_date'] >= end) 
                                            )]

  # Работа с текущим интервалом
  # Подсчет выполненных и просроченных задач
  df_tasks_i_complete = df_tasks_interval.dropna(subset=['complete_date'])
  df_tasks_i_success = df_tasks_i_complete.groupby('worker_id').size().reset_index(name='complete_tasks')

  # Просроченных
  # Оговорка - считаются таковыми и в сравнении по часам
  df_tasks_i_expired = df_tasks_interval[(df_tasks_interval['end'] < now)
                                        & (df_tasks_interval['complete_date'].isna()
                                        | (df_tasks_interval['end'] < df_tasks_interval['complete_date']))
                                          ]
  df_tasks_i_expired_res = df_tasks_i_expired.groupby('worker_id').size().reset_index(name='expired_tasks')

  # % Просрочено задач за все время
  # Просрочено за все время
  df_tasks_all_time_expired = df_tasks_all_time[(df_tasks_all_time['end'] < now)
                                                    & (df_tasks_all_time['complete_date'].isna()
                                                    | (df_tasks_all_time['end'] < df_tasks_all_time['complete_date']))
                                                    ]
  df_tasks_all_time_expired_res = df_tasks_all_time_expired.groupby('worker_id').size().reset_index(name='expired_all_time_tasks')

  # Назначено за все время
  df_tasks_all_time_assigned = df_tasks_all_time.groupby('worker_id').size().reset_index(name='assigned_all_time_tasks')

  # Итого процент просроченных за все время (отношение просроченных задач к общему числу)
  df_tasks_all_time_expired_percent = df_tasks_all_time_assigned.merge(df_tasks_all_time_expired_res, how='outer', on='worker_id')
  df_tasks_all_time_expired_percent = df_tasks_all_time_expired_percent.assign(percent=round((df_tasks_all_time_expired_percent["expired_all_time_tasks"]
                                                                                      / df_tasks_all_time_expired_percent["assigned_all_time_tasks"])
                                                                                    * 100, 2))

  # df_tasks_all_time.rename(columns={'worker_id': 'user_id'}, inplace=True)

  df_tasks_all_time_expired_percent.rename(columns={'worker_id': 'user_id'}, inplace=True)
  
  # Встречи/Показы - complete - состоявшиеся 
  df_meetings = get_df_from_table('meetings', engine)
  df_meetings['end'] = pd.to_datetime(df_meetings['end'])
  df_meetings['start'] = pd.to_datetime(df_meetings['start'])
  df_meetings = df_meetings[(df_meetings['start'] >= start)
                          & (df_meetings['start'] <= end)
                          ]
  df_meetings_complete = df_meetings[df_meetings['complete'] == 1]

  df_meetings_complete = df_meetings_complete.groupby('user_id').size().reset_index(name='complete_meet')
  # All Join
  # rating_df = df_agents.merge(result_deals, how='outer', on='user_id')
  rating_df = result_deals.merge(df_tasks_all_time_expired_percent, how='outer', on='user_id')
  rating_df = rating_df.merge(df_meetings_complete, how='outer', on='user_id')

  return rating_df[['username', 'success', 'recom', 'convers', 'assigned_all_time_tasks', 'expired_all_time_tasks', 'percent', 'complete_meet']]
  