from sqlalchemy import create_engine
from config import USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME


def get_engine():
    """
    `mysql+pymysql` - это драйвер для MySQL
    `username:password` - имя пользователя и пароль для доступа к базе данных
    `host:port` - адрес и порт сервера MySQL
    `database_name` - имя базы данных

    :return: engine
    """
    return create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}")
