import streamlit as st
from src.menu import menu_key, close_menu
from src.reports import GROUPS

def show_analysis_page():
    with st.popover("Анализ", width="stretch", key=menu_key("analysis_menu")):
        for index, (group, reports) in enumerate(GROUPS.items()):
            if index:
                st.divider()
            st.caption(group)
            for report in reports:
                if st.button(report, width="stretch"):
                    st.session_state.report = report
                    st.session_state.page = "report"
                    close_menu("analysis_menu")
