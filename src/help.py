import streamlit as st

def show_help_page():
    if st.button("Помощь", width="stretch"):
        st.session_state.page = "help"
        st.rerun()