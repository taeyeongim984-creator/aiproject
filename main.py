import streamlit as st
st.title('나의 첫 시 만들기')
a=st.text_input('이름을 입력하세요!')
st.selectbox('세가지의 주제를 입력하세요')
st.button('만들기 생성')
