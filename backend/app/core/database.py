import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "desenrola"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "cursorclass": DictCursor,
    "autocommit": False,
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

# Banco de dados — conexao MySQL e dependencia injetada nas rotas

