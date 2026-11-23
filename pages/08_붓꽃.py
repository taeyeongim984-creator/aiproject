
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# CSV 파일 경로: pages 폴더의 상위 폴더
csv_path = Path(__file__).resolve().parent.parent / "Iris.csv"

# CSV 파일 불러오기
try:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, encoding="cp949")

# 열 이름 앞뒤의 공백 제거
df.columns = df.columns.str.strip()

# 그래프에 필요한 열이 있는지 확인
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일의 열 이름을 확인해 주세요. "
        f"현재 열 이름: {list(df.columns)}"
    )
    st.stop()

# 필요한 열만 사용하고 결측치 제거
df = df[required_columns].dropna()

# 입력 범위 계산
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())
width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())
