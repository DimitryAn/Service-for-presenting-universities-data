import io
import pandas as pd
import streamlit as st
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from src.filters import filters_list, filters_name
from src.menu import menu_key, close_menu

# длинные названия рубрик не должны обрезаться
COLUMNS = {"Наименование рубрики": st.column_config.TextColumn(width=500)}

@st.cache_data
def csv_file(df, heading):
    # строки заголовка стоят над таблицей
    return ("\n".join(heading) + "\n" + df.to_csv(index=False)).encode("utf-8-sig")

def number_columns(df):
    # номера колонок с числами и с кодами из цифр: в файлах прижимаем их вправо
    numbers = []
    for number, column in enumerate(df.columns):
        values = df[column].dropna()
        if len(values) and all(str(value).isdigit() for value in values):
            numbers.append(number)
    return numbers

@st.cache_data
def html_file(df, heading):
    style = "".join(f"td:nth-child({number + 1}) {{text-align: right}}"
                    for number in number_columns(df))
    lines = f"<h3>{heading[0]}</h3>" + "".join(f"<p>{line}</p>" for line in heading[1:])
    # без меты кириллица открывается кракозябрами
    return f'<meta charset="utf-8"><style>{style}</style>' + lines + df.to_html(index=False)

# готовые файлы запоминаем, чтобы не собирать их при каждой отрисовке
@st.cache_data
def word_file(df, heading):
    document = Document()
    document.add_heading(heading[0], level=1)
    for line in heading[1:]:
        document.add_paragraph(line)
    table = document.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for cell, column in zip(table.rows[0].cells, df.columns):
        cell.text = str(column)
    numbers = number_columns(df)
    for row in df.itertuples(index=False):
        for number, (cell, value) in enumerate(zip(table.add_row().cells, row)):
            cell.text = str(value)
            if number in numbers:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()

@st.cache_data
def excel_file(df, heading):
    buffer = io.BytesIO()
    # таблица начинается через строку после заголовка
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False, startrow=len(heading) + 1)
        sheet = writer.sheets["Sheet1"]
        for number, line in enumerate(heading, start=1):
            sheet[f"A{number}"] = line
    return buffer.getvalue()

def records_line(df):
    return f"Всего записей в таблице: {len(df)}"

def show_save_page(df, name, title, records):
    # над таблицей в файле стоит ее название, под ним условия фильтра и число записей
    heading = [title] + filters_list()
    if records:
        heading.append(records_line(df))
    files = [
        ("CSV", ".csv", csv_file(df, heading)),
        ("Excel", ".xlsx", excel_file(df, heading)),
        ("HTML", ".html", html_file(df, heading)),
        ("Word", ".docx", word_file(df, heading)),
    ]
    with st.popover("Сохранить", width="stretch", key=menu_key("save_menu")):
        for label, suffix, data in files:
            if st.download_button(label, data, name + suffix, width="stretch"):
                close_menu("save_menu")

def show_dataframe(df, name, title="", records=False):
    # в имени файла фильтры коротко, в заголовке внутри него - с названиями уровней
    # заголовок, число записей и кнопка сохранения стоят в одной строке
    left, middle, right = st.columns([6, 2, 1], vertical_alignment="center")
    with left:
        st.markdown(f"###### {title or name}")
    with middle:
        if records:
            # прижимаем число к правому краю, чтобы оно стояло рядом с кнопкой
            st.markdown(f"<h6 style='text-align: right'>{records_line(df)}</h6>",
                        unsafe_allow_html=True)
    with right:
        show_save_page(df, name + filters_name(), title or name, records)
    # таблицы с парой колонок не растягиваем на весь экран
    width = "content" if len(df.columns) <= 6 else "stretch"
    with st.container(height="stretch"):
        st.dataframe(df, width=width, height="stretch", hide_index=True, column_config=COLUMNS)
