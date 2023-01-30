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

deals = get_df_from_table('meetings', engine)
deals.to_csv('./jupyter/meetings.csv')
