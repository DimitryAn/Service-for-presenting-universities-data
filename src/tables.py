import streamlit as st
from src.db import read_table
from src.filters import filter_table
from src.menu import menu_key, close_menu
from src.sort import sort_order
from src.view import show_dataframe

TABLES = {
    "Информация НИР по грантам": "gr_pr",
    "Информации НИР по НТП": "ntp_pr",
    "Информация НИР по темпланам": "tp_pr",
    "ВУЗы": "vuz",
    "Рубрики ГРНТИ": "grntirub",
}

SUMMARY = "Сводные показатели"

KEYS = {
    "gr_pr": ["Код конкурса", "Код НИР"],
    "ntp_pr": ["Код НТП", "Код НИР"],
    "tp_pr": ["Код вуза", "Код НИР"],
    "vuz": ["Код вуза"],
    "grntirub": ["Код рубрики"],
}

def show_tables_page():
    with st.popover("Таблицы", width="stretch", key=menu_key("tables_menu")):
        for tbl in TABLES:
            if st.button(tbl, width="stretch"):
                st.session_state.selected_table = tbl
                st.session_state.page = "tables"
                close_menu("tables_menu")
        st.divider()
        if st.button(SUMMARY, width="stretch"):
            st.session_state.page = "summary"
            close_menu("tables_menu")

def show_table(tbl):
    table = TABLES[tbl]
    df = filter_table(read_table(table, sort_order(KEYS[table])))
    show_dataframe(df, tbl, f"Таблица: {tbl}")
