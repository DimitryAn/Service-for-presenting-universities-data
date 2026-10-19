import io
import streamlit as st
from docx import Document
from src.filters import filters_name

# длинные названия рубрик не должны обрезаться
COLUMNS = {"Наименование рубрики": st.column_config.TextColumn(width=500)}

@st.cache_data
def html_file(df):
    # без меты кириллица открывается кракозябрами
    return '<meta charset="utf-8">' + df.to_html(index=False)

# готовые файлы запоминаем, чтобы не собирать их при каждой отрисовке
@st.cache_data
def word_file(df):
    document = Document()
    table = document.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for cell, column in zip(table.rows[0].cells, df.columns):
        cell.text = str(column)
    for row in df.itertuples(index=False):
        for cell, value in zip(table.add_row().cells, row):
            cell.text = str(value)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()

@st.cache_data
def excel_file(df):
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    return buffer.getvalue()

def show_save_page(df, name):
    files = [
        ("CSV", df.to_csv(index=False).encode("utf-8-sig"), ".csv"),
        ("Excel", excel_file(df), ".xlsx"),
        ("HTML", html_file(df), ".html"),
        ("Word", word_file(df), ".docx"),
    ]
    with st.popover("Сохранить", width="stretch"):
        for label, data, suffix in files:
            st.download_button(label, data, name + suffix, width="stretch")

def show_dataframe(df, name, title=""):
    # заголовок и кнопка сохранения стоят в одной строке
    left, right = st.columns([5, 1], vertical_alignment="center")
    with left:
        st.markdown(f"###### {title or name}")
    with right:
        show_save_page(df, name + filters_name())
    # таблицы с парой колонок не растягиваем на весь экран
    width = "content" if len(df.columns) <= 6 else "stretch"
    with st.container(height="stretch"):
        st.dataframe(df, width=width, height="stretch", hide_index=True, column_config=COLUMNS)
