import streamlit as st

DUMMY_CREDENTIALS = "admin"
LOGIN_FROM_WIDTH = 0.3
DUMMY_LEFT_SPACE_WIDTH = 0.4
DUMMY_RIGHT_SPACE_WIDTH = 0.3

def auth() -> bool:
    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([DUMMY_LEFT_SPACE_WIDTH,LOGIN_FROM_WIDTH,DUMMY_RIGHT_SPACE_WIDTH])
    with col2:
        st.title("Вход в систему")
        with st.form("login_form",width="content"):
            login = st.text_input(label="Введите логин",type="default")    
            password = st.text_input(label="Введите пароль",type="password")  
            clicked = st.form_submit_button("Войти")
            
        if clicked:
            if login == password and login == DUMMY_CREDENTIALS:
                return True
            st.error("Неверный пароль")
        return False
