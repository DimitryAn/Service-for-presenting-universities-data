from src.db import read_query
from src.filters import filter_table, grnti_where
from src.sort import sort_order
from src.view import show_dataframe

QUERY = """
SELECT
    v."Код вуза",
    v."Вуз",
    COALESCE(gr.kol, 0) AS "НИР по грантам",
    COALESCE(gr.summa, 0) AS "Финансирование по грантам",
    COALESCE(ntp.kol, 0) AS "НИР по НТП",
    COALESCE(ntp.summa, 0) AS "Финансирование по НТП",
    COALESCE(tp.kol, 0) AS "НИР по темпланам",
    COALESCE(tp.summa, 0) AS "Финансирование по темпланам"
FROM vuz v
LEFT JOIN (SELECT "Код вуза" AS kod, COUNT(*) AS kol, SUM("Объем гранта") AS summa
           FROM gr_pr {grnti} GROUP BY "Код вуза") gr ON gr.kod = v."Код вуза"
LEFT JOIN (SELECT "Код вуза" AS kod, COUNT(*) AS kol, SUM("Объем финансирования") AS summa
           FROM ntp_pr {grnti} GROUP BY "Код вуза") ntp ON ntp.kod = v."Код вуза"
LEFT JOIN (SELECT "Код вуза" AS kod, COUNT(*) AS kol, SUM("Объем финансирования") AS summa
           FROM tp_pr {grnti} GROUP BY "Код вуза") tp ON tp.kod = v."Код вуза"
WHERE gr.kod IS NOT NULL OR ntp.kod IS NOT NULL OR tp.kod IS NOT NULL
"""

def show_summary():
    grnti, codes = grnti_where()
    df = read_query(QUERY.format(grnti=grnti) + sort_order(["Код вуза"]), codes * 3)
    df = filter_table(df)
    show_dataframe(df, "Сводные показатели")
