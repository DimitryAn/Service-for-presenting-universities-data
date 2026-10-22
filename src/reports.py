from src.db import read_query
from src.filters import filters_where, grnti_like
from src.sort import sort_order
from src.view import show_dataframe

NIR = """
SELECT 'Гранты' AS "Форма финансирования",
       v."Федеральный округ", v."Субъект федерации", v."Город", v."Вуз",
       gr."Руководитель НИР", gr."Код ГРНТИ", gr."Объем гранта" AS "Финансирование"
FROM gr_pr gr JOIN vuz v ON v."Код вуза" = gr."Код вуза"
UNION ALL
SELECT 'НТП',
       v."Федеральный округ", v."Субъект федерации", v."Город", v."Вуз",
       ntp."Руководитель НИР", ntp."Код ГРНТИ", ntp."Объем финансирования"
FROM ntp_pr ntp JOIN vuz v ON v."Код вуза" = ntp."Код вуза"
UNION ALL
SELECT 'Темпланы',
       v."Федеральный округ", v."Субъект федерации", v."Город", v."Вуз",
       tp."Руководитель НИР", tp."Код ГРНТИ", tp."Объем финансирования"
FROM tp_pr tp JOIN vuz v ON v."Код вуза" = tp."Код вуза"
"""

# итоги по всем формам финансирования сразу
TOTALS = """COUNT(*) AS "Количество НИР",
               SUM("Финансирование") AS "Сумма финансирования"
"""

# количество и финансирование по каждой форме отдельно
FORMS = """SUM("Форма финансирования" = 'Гранты') AS "НИР по грантам",
               SUM(CASE WHEN "Форма финансирования" = 'Гранты' THEN "Финансирование" ELSE 0 END) AS "Финансирование по грантам",
               SUM("Форма финансирования" = 'НТП') AS "НИР по НТП",
               SUM(CASE WHEN "Форма финансирования" = 'НТП' THEN "Финансирование" ELSE 0 END) AS "Финансирование по НТП",
               SUM("Форма финансирования" = 'Темпланы') AS "НИР по темпланам",
               SUM(CASE WHEN "Форма финансирования" = 'Темпланы' THEN "Финансирование" ELSE 0 END) AS "Финансирование по темпланам"
"""

# сколько нир по рубрике в каждой форме финансирования
NUMBERS = """SUM("Форма финансирования" = 'Гранты') AS "НИР по грантам",
               SUM("Форма финансирования" = 'НТП') AS "НИР по НТП",
               SUM("Форма финансирования" = 'Темпланы') AS "НИР по темпланам"
"""

# коды в одной ячейке разделены по-разному, приводим разделители к запятой
CODES = """',' || REPLACE(REPLACE(REPLACE(nir."Код ГРНТИ", ';', ','), ':', ','), ' ', ',')"""

REPORTS = {
    "По субъектам федерации": """
        SELECT "Субъект федерации",
               {totals},
               {forms}
        FROM nir
        {where}
        GROUP BY "Субъект федерации"
        {order}
    """,
    "По городам": """
        SELECT "Субъект федерации", "Город",
               {totals},
               {forms}
        FROM nir
        {where}
        GROUP BY "Субъект федерации", "Город"
        {order}
    """,
    "По формам финансирования": """
        SELECT "Форма финансирования",
               {totals}
        FROM nir
        {where}
        GROUP BY "Форма финансирования"
        {order}
    """,
    "По руководителям": """
        SELECT "Руководитель НИР", "Вуз",
               {totals},
               {forms}
        FROM nir
        {where}
        GROUP BY "Руководитель НИР", "Вуз"
        HAVING COUNT(*) > 1
        {order}
    """,
    "По рубрикам ГРНТИ": """
        SELECT r."Код рубрики", r."Наименование рубрики",
               {numbers}
        FROM grntirub r JOIN nir
             -- нир попадает в рубрику, если с ее номера начинается код, подходящий
             -- под фильтр; даже если таких кодов два, рубрика получит одну строку
             ON r."Код рубрики" LIKE '{rubric}'
                AND {codes} LIKE '%,' || r."Код рубрики" || '{tail}'
        {where}
        GROUP BY r."Код рубрики", r."Наименование рубрики"
        {order}
    """,
}

# в меню отчеты разделены на две части
GROUPS = {
    "Отчеты по сводным показателям": ["По субъектам федерации", "По городам", "По формам финансирования"],
    "Отчеты по базам НИР": ["По руководителям", "По рубрикам ГРНТИ"],
}

KEYS = {
    "По субъектам федерации": ["Субъект федерации"],
    "По городам": ["Субъект федерации", "Город"],
    "По формам финансирования": ["Форма финансирования"],
    "По руководителям": ["Руководитель НИР", "Вуз"],
    "По рубрикам ГРНТИ": ["Код рубрики"],
}

def add_total(df):
    # итоги считаются по тому, что осталось после фильтров
    total = df.sum(numeric_only=True)
    df.loc[len(df)] = {column: total.get(column, "") for column in df.columns}
    df.iloc[-1, 0] = "Итого"
    return df

def show_report(choice):
    where, values = filters_where()
    rubric, tail = grnti_like()
    query = f"WITH nir AS ({NIR}) " + REPORTS[choice].format(
        totals=TOTALS, forms=FORMS, numbers=NUMBERS, codes=CODES, rubric=rubric, tail=tail,
        where=where, order=sort_order(KEYS[choice]))
    df = add_total(read_query(query, values))
    show_dataframe(df, choice)
