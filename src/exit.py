import streamlit as st

def show_exit_page():
    if st.button("Выход", width="stretch"):
        st.session_state.page = "exit"
        st.rerun()