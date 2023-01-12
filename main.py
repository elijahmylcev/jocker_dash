from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME
import pandas as pd

# - `mysql+pymysql` - это драйвер для MySQL, который мы установили ранее
# - `username:password` - имя пользователя и пароль для доступа к базе данных
# - `host:port` - адрес и порт сервера MySQL
# - `database_name` - имя базы данных, к которой мы хотим подключиться
def select_all(table_name):
  engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}")
  result_df = pd.read_sql(f'SELECT * FROM {table_name}', engine)
  return result_df
