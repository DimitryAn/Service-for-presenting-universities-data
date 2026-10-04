import streamlit as st
from src.reports import GROUPS

def show_analysis_page():
    with st.popover("Анализ", width="stretch"):
        st.caption("Выберите отчет:")
        if st.button("Сводные показатели", width="stretch"):
            st.session_state.page = "summary"
            st.rerun()
        for group in GROUPS:
            if st.button(group, key=f"rep_{group}", width="stretch"):
                st.session_state.report_group = group
                st.session_state.page = "report"
                st.rerun()
