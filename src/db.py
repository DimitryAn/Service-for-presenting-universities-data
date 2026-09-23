import sqlite3
import pandas as pd
from config import DB_PATH


def read_table(table):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"""SELECT * FROM {table}""", conn)
    conn.close()
    return df
