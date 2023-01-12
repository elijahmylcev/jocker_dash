from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME
import pandas as pd
from functions import get_df_from_table

# - `mysql+pymysql` - это драйвер для MySQL, который мы установили ранее
# - `username:password` - имя пользователя и пароль для доступа к базе данных
# - `host:port` - адрес и порт сервера MySQL
# - `database_name` - имя базы данных, к которой мы хотим подключиться
engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}")

deals = get_df_from_table('deals', engine)
print(deals)