import streamlit as st
from src.db import read_table

LEVELS = ["Федеральный округ", "Субъект федерации", "Город", "Вуз"]

def geo():
    if "geo" not in st.session_state:
        st.session_state.geo = {level: "Все" for level in LEVELS}
    return st.session_state.geo

def filter_vuz(vuz, levels):
    chosen = geo()
    for level in levels:
        if chosen[level] != "Все":
            vuz = vuz[vuz[level] == chosen[level]]
    return vuz

def pick_level(level, choice):
    chosen = geo()
    chosen[level] = choice
    number = LEVELS.index(level)
    for lower in LEVELS[number + 1:]:
        chosen[lower] = "Все"
    if choice != "Все":
        vuz = read_table("vuz")
        row = vuz[vuz[level] == choice].iloc[0]
        for upper in LEVELS[:number]:
            chosen[upper] = row[upper]

def show_geo_page():
    chosen = geo()
    vuz = read_table("vuz")
    with st.popover("География", width="stretch"):
        st.caption("Выберите уровень:")
        for level in LEVELS:
            rows = filter_vuz(vuz, LEVELS[:LEVELS.index(level)])
            options = ["Все"] + sorted(rows[level].dropna().unique())
            choice = st.selectbox(level, options, index=options.index(chosen[level]))
            if choice != chosen[level]:
                pick_level(level, choice)
                st.rerun()
        if st.button("Сбросить", width="stretch"):
            st.session_state.geo = {level: "Все" for level in LEVELS}
            st.rerun()

def geo_where():
    chosen = geo()
    parts = [f'"{level}" = ?' for level in LEVELS if chosen[level] != "Все"]
    values = [chosen[level] for level in LEVELS if chosen[level] != "Все"]
    if parts:
        return "WHERE " + " AND ".join(parts), values
    return "", []

def selected_codes():
    chosen = geo()
    if all(chosen[level] == "Все" for level in LEVELS):
        return None
    return list(filter_vuz(read_table("vuz"), LEVELS)["Код вуза"])
