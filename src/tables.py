import streamlit as st

TABLES = {
    "Информация НИР по грантам": "gr_pr",
    "Информации НИР по НТП": "ntp_pr",
    "Информация НИР по темпланам": "tp_pr",
    "ВУЗы": "vuz",
    "Рубрики ГРНТИ": "grntirub",
}

def show_tables_page():
    with st.popover("Таблицы", width="stretch"):
        st.caption("Выберите таблицу:")
        for t in TABLES:
            if st.button(t, key=f"tbl_{t}", width="stretch"):
                st.session_state.selected_table = t
                st.session_state.page = "tables"
                st.rerun()