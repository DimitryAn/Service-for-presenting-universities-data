import streamlit as st

def show_menu():
    if st.button("Меню", width="stretch"):
        st.session_state.page = "home"
        st.rerun()