import streamlit as st
from src.db import read_query
from src.geo import geo_where
from src.sort import sort_order

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

GROUPS = {
    "Отчеты по сводным показателям": {
        "По субъектам федерации": """
            SELECT "Субъект федерации",
                   COUNT(*) AS "Количество НИР",
                   SUM("Финансирование") AS "Сумма финансирования"
            FROM nir
            {where}
            GROUP BY "Субъект федерации"
            {order}
        """,
        "По городам": """
            SELECT "Субъект федерации", "Город",
                   COUNT(*) AS "Количество НИР",
                   SUM("Финансирование") AS "Сумма финансирования"
            FROM nir
            {where}
            GROUP BY "Субъект федерации", "Город"
            {order}
        """,
        "По формам финансирования": """
            SELECT "Форма финансирования",
                   COUNT(*) AS "Количество НИР",
                   SUM("Финансирование") AS "Сумма финансирования"
            FROM nir
            {where}
            GROUP BY "Форма финансирования"
            {order}
        """,
    },
    "Отчеты по базам НИР": {
        "Руководители с несколькими НИР": """
            SELECT "Руководитель НИР",
                   COUNT(*) AS "Количество НИР",
                   SUM("Финансирование") AS "Сумма финансирования"
            FROM nir
            {where}
            GROUP BY "Руководитель НИР"
            HAVING COUNT(*) > 1 AND "Руководитель НИР" IS NOT NULL
            {order}
        """,
        "Распределение НИР по рубрикам ГРНТИ": """
            SELECT SUBSTR(nir."Код ГРНТИ", 1, 2) AS "Код рубрики",
                   r."Наименование рубрики",
                   COUNT(*) AS "Количество НИР",
                   SUM("Финансирование") AS "Сумма финансирования"
            FROM nir LEFT JOIN grntirub r ON r."Код рубрики" = SUBSTR(nir."Код ГРНТИ", 1, 2)
            {where}
            GROUP BY "Код рубрики", "Наименование рубрики"
            HAVING "Код рубрики" IS NOT NULL
            {order}
        """,
    },
}

KEYS = {
    "По субъектам федерации": ["Субъект федерации"],
    "По городам": ["Субъект федерации", "Город"],
    "По формам финансирования": ["Форма финансирования"],
    "Руководители с несколькими НИР": ["Руководитель НИР"],
    "Распределение НИР по рубрикам ГРНТИ": ["Код рубрики"],
}

def show_report(group):
    reports = GROUPS[group]
    names = list(reports)
    if st.session_state.report not in names:
        st.session_state.report = names[0]
    choice = st.radio("Отчет", names, index=names.index(st.session_state.report), horizontal=True)
    if choice != st.session_state.report:
        st.session_state.report = choice
        st.rerun()
    where, values = geo_where()
    query = f"WITH nir AS ({NIR}) " + reports[choice].format(where=where, order=sort_order(KEYS[choice]))
    st.dataframe(read_query(query, values), width="stretch", height=700, hide_index=True)
