import streamlit as st
from src.menu import menu_key, close_menu

SORTS = ["Без сортировки", "По возрастанию", "По убыванию"]

def show_sort_page():
    with st.popover("Сортировка по ключу", width="stretch", key=menu_key("sort_menu")):
        for sort in SORTS:
            if st.button(sort, width="stretch", disabled=sort == st.session_state.sort):
                st.session_state.sort = sort
                close_menu("sort_menu")

def sort_order(columns):
    if st.session_state.sort == "Без сортировки":
        return ""
    parts = []
    for column in columns:
        parts.append(f'CAST("{column}" AS INTEGER)')
        parts.append(f'"{column}"')
    if st.session_state.sort == "По убыванию":
        parts = [part + " DESC" for part in parts]
    return " ORDER BY " + ", ".join(parts)
