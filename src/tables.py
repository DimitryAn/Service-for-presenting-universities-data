import streamlit as st

TABLES = ["Информация НИР по грантам", "Информации НИР по НТП", "Информация НИР по темпланам", "ВУЗы"]

def show_tables_page():
    with st.popover("Таблицы", width="stretch"):
        st.caption("Выберите таблицу:")
        for t in TABLES:
            if st.button(t, key=f"tbl_{t}", width="stretch"):
                st.session_state.selected_table = t
                st.session_state.page = "tables"
                st.rerun()