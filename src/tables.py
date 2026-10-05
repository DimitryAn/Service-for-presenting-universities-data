import streamlit as st
from src.db import read_table
from src.geo import selected_codes
from src.sort import sort_order

TABLES = {
    "Информация НИР по грантам": "gr_pr",
    "Информации НИР по НТП": "ntp_pr",
    "Информация НИР по темпланам": "tp_pr",
    "ВУЗы": "vuz",
    "Рубрики ГРНТИ": "grntirub",
}

KEYS = {
    "gr_pr": ["Код конкурса", "Код НИР"],
    "ntp_pr": ["Код НТП", "Код НИР"],
    "tp_pr": ["Код вуза", "Код НИР"],
    "vuz": ["Код вуза"],
    "grntirub": ["Код рубрики"],
}

def show_tables_page():
    with st.popover("Таблицы", width="stretch"):
        st.caption("Выберите таблицу:")
        for t in TABLES:
            if st.button(t, key=f"tbl_{t}", width="stretch"):
                st.session_state.selected_table = t
                st.session_state.page = "tables"
                st.rerun()

def show_table(tbl):
    table = TABLES[tbl]
    df = read_table(table, sort_order(KEYS[table]))
    codes = selected_codes()
    if codes is not None and table != "grntirub":
        df = df[df["Код вуза"].isin(codes)]
    st.dataframe(df, width="stretch", height=700, hide_index=True)
