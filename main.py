import streamlit as st
from src.tables import show_tables_page, show_table
from src.analysis import show_analysis_page
from src.exit import show_exit_page
from src.help import show_help_page

st.set_page_config(page_title="University Viewer", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None

col1, col2, col3, col4 = st.columns(4)

with col1:
    show_analysis_page()

with col2:
    show_tables_page()
                
with col3:
    show_exit_page()

with col4:
    show_help_page()
        
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
    st.header("До свидания")
    #st.stop()