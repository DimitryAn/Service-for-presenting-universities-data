import sqlite3
import pandas as pd
from config import DB_PATH


def read_query(query, values=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=values)
    conn.close()
    return df


def read_table(table, order=""):
    return read_query(f"""SELECT * FROM {table} {order}""")
