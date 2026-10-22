import streamlit as st
from config import PROJECT_DIR
from src.analysis import show_analysis_page
from src.auth import auth
from src.filters import show_filter_page
from src.menu import show_help_page, show_exit_page
from src.reports import show_report
from src.sort import show_sort_page
from src.summary import show_summary
from src.tables import show_tables_page, show_table

st.set_page_config(page_title="Анализ сводных показателей выполнения НИР", layout="wide")

START = {"logged_in": False, "page": "home", "sort": "Без сортировки"}
for key, value in START.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.logged_in:
    if auth():
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

styles = (PROJECT_DIR / "src" / "style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{styles}</style>", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    show_tables_page()

with col2:
    show_analysis_page()

with col3:
    show_filter_page()

with col4:
    show_sort_page()

with col5:
    show_help_page()

with col6:
    show_exit_page()

page = st.session_state.page

if page == "home":
    st.markdown("###### Добро пожаловать.")
    st.markdown("Выберите раздел в панели сверху.")

elif page == "tables":
    show_table(st.session_state.selected_table)

elif page == "summary":
    show_summary()

elif page == "report":
    show_report(st.session_state.report)

elif page == "help":
    st.markdown("###### Помощь")
    st.markdown("Инструкция по использованию сервиса.")
