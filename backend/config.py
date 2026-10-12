import os
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_management")

db_pool = pooling.MySQLConnectionPool(
    pool_name="sqlsphere_pool",
    pool_size=5,
    pool_reset_session=True,
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    autocommit=True
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")