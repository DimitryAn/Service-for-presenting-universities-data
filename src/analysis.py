import streamlit as st

def show_analysis_page():
    if st.button("Анализ", width="stretch"):
        st.rerun()