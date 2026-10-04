import streamlit as st
from src.tables import show_tables_page, show_table
from src.analysis import show_analysis_page
from src.exit import show_exit_page
from src.help import show_help_page
from src.auth import auth

st.set_page_config(page_title="University Viewer", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None

if not st.session_state.logged_in:
    is_logged = auth()
    if is_logged:
        st.session_state.logged_in = True
        st.rerun()
    else:
        st.stop()
        
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    show_tables_page()
    
with col2:
    show_analysis_page()
              
with col3:
    show_help_page()

with col4:
    show_exit_page()
        
current_page = st.session_state.page


if current_page == "home":
    st.markdown("##### Добро пожаловать.")
    st.markdown("Выберите раздел в панели сверху.")

elif current_page == "analysis":
    st.markdown("##### Анализ")
    st.markdown("Здесь будет аналитика по данным.")

elif current_page == "tables":
    tbl = st.session_state.selected_table
    if tbl:
        st.markdown(f"##### Таблица: {tbl}")
        show_table(tbl)
    else:
        st.markdown("##### Таблицы")
        st.info("Выберите таблицу в меню сверху.")

elif current_page == "help":
    st.markdown("##### Помощь")
    st.markdown("Инструкция по использованию сервиса.")

elif current_page == "exit":
    st.session_state.logged_in = False
    st.session_state.page = "home"
    st.session_state.selected_table = None
    st.rerun()