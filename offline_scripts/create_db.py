import sqlite3
import pandas as pd
from config import DATA_DIR, DB_PATH

files = {"vuz": "VUZ.XLS", "gr_pr": "Gr_pr.XLS", "ntp_pr": "Ntp_pr.XLS", "tp_pr": "Tp_pr.XLS", "grntirub": "grntirub.XLS"}

conn = sqlite3.connect(DB_PATH)

for table, file_name in files.items():
    df = pd.read_excel(DATA_DIR / file_name, engine="xlrd")
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(table, len(df))

conn.close()