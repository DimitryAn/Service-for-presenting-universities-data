import re
import streamlit as st
from src.db import read_table, read_query
from src.menu import menu_key, close_menu

LEVELS = ["Федеральный округ", "Субъект федерации", "Город", "Вуз"]
PARTS = ["ГРНТИ 1", "ГРНТИ 2", "ГРНТИ 3"]

def empty_filters():
    return {level: "Все" for level in LEVELS} | {part: "" for part in PARTS}

def filters():
    if "filters" not in st.session_state:
        st.session_state.filters = empty_filters()
    return st.session_state.filters

def draft():
    if "filters_draft" not in st.session_state:
        st.session_state.filters_draft = dict(filters())
    return st.session_state.filters_draft

def filter_vuz(vuz, levels, chosen):
    for level in levels:
        if chosen[level] != "Все":
            vuz = vuz[vuz[level] == chosen[level]]
    return vuz

def pick_level(level, choice):
    chosen = draft()
    chosen[level] = choice
    number = LEVELS.index(level)
    for lower in LEVELS[number + 1:]:
        chosen[lower] = "Все"
    if choice != "Все":
        vuz = read_table("vuz")
        row = vuz[vuz[level] == choice].iloc[0]
        for upper in LEVELS[:number]:
            chosen[upper] = row[upper]

def show_filter_page():
    chosen = draft()
    vuz = read_table("vuz")
    with st.popover("Фильтр", width="stretch", key=menu_key("filter_menu")):
        # два фильтра стоят рядом в рамках, иначе выпадайка не помещается в экран
        left, right = st.columns(2, border=True)
        with left:
            st.caption("Группа вузов:")
            for level in LEVELS:
                rows = filter_vuz(vuz, LEVELS[:LEVELS.index(level)], chosen)
                options = ["Все"] + sorted(rows[level].dropna().unique())
                choice = st.selectbox(level, options, index=options.index(chosen[level]),
                                      placeholder="Выберите опцию")
                if choice != chosen[level]:
                    pick_level(level, choice)
                    st.rerun()
        with right:
            st.caption("Код ГРНТИ:")
            columns = st.columns([3, 1, 3, 1, 3])
            number = st.session_state.get("filter_menu", 0)
            for index, part in enumerate(PARTS):
                with columns[index * 2]:
                    # номер тот же, что у выпадайки: после сброса поля создаются заново
                    key = f"{part}_{number}"
                    if key not in st.session_state:
                        st.session_state[key] = chosen[part]
                    chosen[part] = st.text_input(part, max_chars=2, placeholder="**", key=key,
                                                 label_visibility="collapsed")
            for index in [1, 3]:
                with columns[index]:
                    st.markdown("###### .")
            # код ГРНТИ состоит из чисел, буквы и знаки в нем не нужны
            wrong = any(not chosen[part].isdigit() for part in PARTS if chosen[part])
            if wrong:
                st.error("В коде ГРНТИ только цифры")
        apply, reset = st.columns(2)
        with apply:
            if st.button("Применить", width="stretch", disabled=wrong):
                st.session_state.filters = dict(chosen)
                close_menu("filter_menu")
        with reset:
            if st.button("Сбросить", width="stretch"):
                st.session_state.filters = empty_filters()
                st.session_state.filters_draft = empty_filters()
                close_menu("filter_menu")

def grnti_parts():
    chosen = filters()
    return [chosen[part] for part in PARTS]

def match_grnti(value, parts):
    if not any(parts):
        return True
    # пустые ячейки приходят как None или NaN
    if not isinstance(value, str):
        return False
    # в одной ячейке бывает несколько кодов через разные разделители
    for code in re.split(r"[,;: ]+", value):
        # добавляем пустые пары, чтобы короткий код не совпал с длинным фильтром
        levels = code.split(".") + ["", ""]
        if all(levels[number].startswith(part) for number, part in enumerate(parts)):
            return True
    return False

def grnti_like():
    # для отчета по рубрикам: отдельно номер рубрики, отдельно остальные цифры кода
    rubric, *levels = grnti_parts()
    while levels and not levels[-1]:
        levels.pop()
    # в каждом уровне кода по две цифры, знак _ заменяет любую из них
    tail = "".join("." + level.ljust(2, "_") for level in levels)
    return rubric + "%", tail + "%"

def filters_list():
    # условия фильтра с названиями уровней: в заголовке файла каждое со своей строки
    chosen = filters()
    parts = [f"{level}: {chosen[level]}" for level in LEVELS if chosen[level] != "Все"]
    code = ".".join(part or "__" for part in grnti_parts()).rstrip("._")
    if code:
        parts.append("Код ГРНТИ: " + code)
    return parts

def filters_name():
    # те же условия покороче, они идут в название файла
    chosen = filters()
    parts = [chosen[level] for level in LEVELS if chosen[level] != "Все"]
    code = ".".join(part or "__" for part in grnti_parts()).rstrip("._")
    if code:
        parts.append("ГРНТИ " + code)
    if parts:
        return " (" + ", ".join(parts) + ")"
    return ""

def grnti_codes():
    parts = grnti_parts()
    if not any(parts):
        return None
    codes = read_query("""
        SELECT "Код ГРНТИ" FROM gr_pr
        UNION SELECT "Код ГРНТИ" FROM ntp_pr
        UNION SELECT "Код ГРНТИ" FROM tp_pr
    """)["Код ГРНТИ"]
    return [code for code in codes if match_grnti(code, parts)]

def in_codes(codes):
    return '"Код ГРНТИ" IN (' + ", ".join(["?"] * len(codes)) + ")"

def grnti_where():
    codes = grnti_codes()
    if codes is None:
        return "", []
    return "WHERE " + in_codes(codes), codes

def filters_where():
    chosen = filters()
    levels = [level for level in LEVELS if chosen[level] != "Все"]
    conditions = [f'"{level}" = ?' for level in levels]
    values = [chosen[level] for level in levels]
    codes = grnti_codes()
    if codes is not None:
        conditions.append(in_codes(codes))
        values = values + codes
    if conditions:
        return "WHERE " + " AND ".join(conditions), values
    return "", []

def selected_codes():
    chosen = filters()
    if all(chosen[level] == "Все" for level in LEVELS):
        return None
    return list(filter_vuz(read_table("vuz"), LEVELS, chosen)["Код вуза"])

def filter_table(df):
    codes = selected_codes()
    if codes is not None and "Код вуза" in df:
        df = df[df["Код вуза"].isin(codes)]
    parts = grnti_parts()
    if any(parts):
        if "Код ГРНТИ" in df:
            df = df[[match_grnti(value, parts) for value in df["Код ГРНТИ"]]]
        if "Код рубрики" in df:
            df = df[[match_grnti(value, parts[:1]) for value in df["Код рубрики"]]]
    return df
