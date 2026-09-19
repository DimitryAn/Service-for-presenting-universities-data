import sqlite3
import pandas as pd
from config import MODIFIED_DATA_DIR, DB_PATH

tables = ["vuz", "gr_pr", "ntp_pr", "tp_pr", "grntirub"]

# первичные ключи таблиц НИР: (группа, код НИР в группе)
keys = {
    "gr_pr": ("Код конкурса", "Код НИР в конкурсе"),
    "ntp_pr": ("Код НТП", "Код НИР в НТП"),
    "tp_pr": ("Код вуза", "Код НИР в вузе")
}

# удаляем старую базу и создаем новую
DB_PATH.unlink(missing_ok=True)
conn = sqlite3.connect(DB_PATH)

# загружаем таблицы из modified data, все значения как текст
for table in tables:
    df = pd.read_excel(MODIFIED_DATA_DIR / f"{table}.xlsx", dtype=str)
    df.to_sql(table, conn, index=False)

# убираем пробелы в начале и в конце всех ячеек, заглушки ??? и - делаем пустыми
for table in tables:
    columns = [row[1] for row in conn.execute(f"""PRAGMA table_info({table})""")]
    for column in columns:
        conn.execute(f"""UPDATE {table} SET "{column}" = TRIM("{column}")""")
        conn.execute(f"""UPDATE {table} SET "{column}" = NULL WHERE "{column}" IN ('???', '-')""")

# заполняем пустые наименования вузов из таблицы vuz по коду вуза
conn.executescript("""
UPDATE gr_pr SET "Сокращенное наименование вуза" = vuz."Сокращенное наименование вуза" FROM vuz WHERE vuz."Код вуза" = gr_pr."Код вуза";
UPDATE tp_pr SET "Сокращенное наименование вуза" = vuz."Сокращенное наименование вуза" FROM vuz WHERE vuz."Код вуза" = tp_pr."Код вуза";
UPDATE ntp_pr SET "Организация-исполнитель" = vuz."Сокращенное наименование вуза" FROM vuz WHERE vuz."Код вуза" = ntp_pr."Код организации-исполнителя";
""")

# исправляем повторяющиеся ключи: повтор получает код = старший код в группе + 1
for table, (group, code) in keys.items():
    conn.execute(f"""UPDATE {table} SET "{code}" = REPLACE("{code}", ' ', '')""")
    seen = set()
    for rowid, group_value, code_value in conn.execute(f"""SELECT rowid, "{group}", "{code}" FROM {table} ORDER BY "{group}", "{code}", rowid""").fetchall():
        if (group_value, code_value) in seen:
            prefix = code_value.rstrip("0123456789")
            max_number = conn.execute(f"""SELECT MAX(CAST(SUBSTR("{code}", ?) AS INTEGER)) FROM {table} WHERE "{group}" = ? AND "{code}" LIKE ?""", (len(prefix) + 1, group_value, prefix + "%")).fetchone()[0]
            code_value = prefix + str(max_number + 1).zfill(len(code_value) - len(prefix))
            conn.execute(f"""UPDATE {table} SET "{code}" = ? WHERE rowid = ?""", (code_value, rowid))
        seen.add((group_value, code_value))

# создаем новые таблицы с первичными ключами и типами колонок
conn.executescript("""
CREATE TABLE vuz_new (
    "Код вуза" TEXT NOT NULL PRIMARY KEY,
    "Сокращенное наименование вуза" TEXT,
    "Наименование вуза" TEXT,
    "Статус" TEXT,
    "Федеральный округ" TEXT,
    "Код субъекта федерации" TEXT,
    "Субъект федерации" TEXT,
    "Город" TEXT,
    "Категория вуза" TEXT,
    "Профиль вуза" TEXT,
    "Полное юридическое наименование вуза" TEXT
);

CREATE TABLE gr_pr_new (
    "Код конкурса" TEXT NOT NULL,
    "Код НИР в конкурсе" TEXT NOT NULL,
    "Сокращенное наименование вуза" TEXT,
    "Руководитель НИР" TEXT,
    "Должность руководителя" TEXT,
    "Ученая степень руководителя" TEXT,
    "Ученое звание руководителя" TEXT,
    "Плановый объем гранта" INTEGER,
    "Код вуза" TEXT,
    "Код ГРНТИ" TEXT,
    "Наименование НИР" TEXT,
    PRIMARY KEY ("Код конкурса", "Код НИР в конкурсе")
);

CREATE TABLE ntp_pr_new (
    "Код НТП" TEXT NOT NULL,
    "Код НИР в НТП" TEXT NOT NULL,
    "Организация-исполнитель" TEXT,
    "Руководитель НИР" TEXT,
    "Должность, степень и звание руководителя" TEXT,
    "Плановое финансирование" INTEGER,
    "Код организации-исполнителя" TEXT,
    "Характер НИР" TEXT,
    "Код ГРНТИ" TEXT,
    "Наименование НИР" TEXT,
    PRIMARY KEY ("Код НТП", "Код НИР в НТП")
);

CREATE TABLE tp_pr_new (
    "Код вуза" TEXT NOT NULL,
    "Код НИР в вузе" TEXT NOT NULL,
    "Сокращенное наименование вуза" TEXT,
    "Руководитель НИР" TEXT,
    "Должность руководителя" TEXT,
    "Плановый объем финансирования" INTEGER,
    "Характер НИР" TEXT,
    "Код ГРНТИ" TEXT,
    "Наименование НИР" TEXT,
    PRIMARY KEY ("Код вуза", "Код НИР в вузе")
);

CREATE TABLE grntirub_new (
    "Код рубрики" TEXT NOT NULL PRIMARY KEY,
    "Наименование рубрики" TEXT
);
""")

# переносим данные в новые таблицы и заменяем ими старые
for table in tables:
    conn.execute(f"""INSERT INTO {table}_new SELECT * FROM {table}""")
    conn.execute(f"""DROP TABLE {table}""")
    conn.execute(f"""ALTER TABLE {table}_new RENAME TO {table}""")
    print(table, conn.execute(f"""SELECT COUNT(*) FROM {table}""").fetchone()[0])

conn.commit()
conn.close()
