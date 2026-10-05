import streamlit as st

SORTS = ["Без сортировки", "По возрастанию", "По убыванию"]

def show_sort_page():
    with st.popover("Сортировка", width="stretch"):
        st.caption("Сортировка по ключу:")
        choice = st.radio("Порядок", SORTS, index=SORTS.index(st.session_state.sort))
        if choice != st.session_state.sort:
            st.session_state.sort = choice
            st.rerun()

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
