import streamlit as st
from src.tables import show_tables_page, show_table
from src.analysis import show_analysis_page
from src.exit import show_exit_page
from src.help import show_help_page
from src.menu import show_menu
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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    show_menu()
    
with col2:
    show_tables_page()
    
with col3:
    show_analysis_page()
              
with col4:
    show_help_page()

with col5:
    show_exit_page()
        
st.write("---")

current_page = st.session_state.page


if current_page == "home":
    st.title("Добро пожаловать")
    st.write("Выберите раздел в панели сверху.")

elif current_page == "analysis":
    st.header("Анализ")
    st.write("Здесь будет аналитика по данным.")

elif current_page == "tables":
    tbl = st.session_state.selected_table
    if tbl:
        st.header(f"Таблица: {tbl}")
        show_table(tbl)
    else:
        st.header("Таблицы")
        st.info("Выберите таблицу в меню сверху.")

elif current_page == "help":
    st.header("Помощь")
    st.write("Инструкция по использованию сервиса.")

elif current_page == "exit":
    st.session_state.logged_in = False
    st.session_state.page = "home"
    st.session_state.selected_table = None
    st.rerun()