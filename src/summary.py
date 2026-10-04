import streamlit as st
from src.db import read_query
from src.geo import selected_codes
from src.sort import sort_order

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
           FROM gr_pr GROUP BY "Код вуза") gr ON gr.kod = v."Код вуза"
LEFT JOIN (SELECT "Код вуза" AS kod, COUNT(*) AS kol, SUM("Объем финансирования") AS summa
           FROM ntp_pr GROUP BY "Код вуза") ntp ON ntp.kod = v."Код вуза"
LEFT JOIN (SELECT "Код вуза" AS kod, COUNT(*) AS kol, SUM("Объем финансирования") AS summa
           FROM tp_pr GROUP BY "Код вуза") tp ON tp.kod = v."Код вуза"
WHERE gr.kod IS NOT NULL OR ntp.kod IS NOT NULL OR tp.kod IS NOT NULL
"""

def show_summary():
    df = read_query(QUERY + sort_order(["Код вуза"]))
    codes = selected_codes()
    if codes is not None:
        df = df[df["Код вуза"].isin(codes)]
    st.dataframe(df, width="stretch", height=700)
