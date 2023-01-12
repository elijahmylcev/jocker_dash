from dotenv import load_dotenv
import os

load_dotenv()

HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
DATABASE_NAME=os.getenv('DATABASE_NAME')
USERNAME=os.getenv('USER_NAME')
PASSWORD=os.getenv('PASSWORD')
