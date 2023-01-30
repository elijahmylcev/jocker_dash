from sqlalchemy import create_engine
from config import USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME
import pandas as pd
from datetime import datetime
import requests

from functions import get_df_from_table, get_agents

# - `mysql+pymysql` - это драйвер для MySQL, который мы установили ранее
# - `username:password` - имя пользователя и пароль для доступа к базе данных
# - `host:port` - адрес и порт сервера MySQL
# - `database_name` - имя базы данных, к которой мы хотим подключиться
engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}")

# Time intercal
start = datetime.strptime('2023-01-01', '%Y-%m-%d')
end = datetime.strptime('2023-01-30', '%Y-%m-%d')
now = datetime.now().strftime("%Y-%m-%d")
print(f'start - {start}; \nend - {end} \nnow - {now}')

deals = get_df_from_table('meetings', engine)
deals.to_csv('./jupyter/meetings.csv')
