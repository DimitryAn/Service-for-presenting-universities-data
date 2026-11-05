import streamlit as st
from config import PROJECT_DIR

HELP_PATH = PROJECT_DIR / "docs" / "help.md"

def menu_key(name):
    # номер в ключе меняется после выбора, и выпадайка закрывается
    return f"{name}_{st.session_state.get(name, 0)}"

def close_menu(name):
    st.session_state[name] = st.session_state.get(name, 0) + 1
    st.rerun()

def show_help_page():
    if st.button("Помощь", width="stretch"):
        st.session_state.page = "help"
        st.rerun()

def show_help():
    # руководство лежит отдельным файлом, ссылки в нем ведут к разделам
    text = HELP_PATH.read_text(encoding="utf-8")
    with st.container(height="stretch", key="help"):
        st.markdown(text, unsafe_allow_html=True)

def show_exit_page():
    if st.button("Выход", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()
