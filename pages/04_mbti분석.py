```python
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="국가별 MBTI 분석",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 국가별 MBTI 비율 분석")
st.write("MBTI 유형을 선택하고, 해당 유형의 비율이 높은 나라와 낮은 나라를 비교해 보세요!")

# CSV 파일은 프로젝트 최상위 폴더에 있어야 합니다.
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "countriesMBTI_16types (6).csv"

MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path)
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    data.columns = data.columns.astype(str).str.strip()

    # 국가 이름 열을 Country로 통일합니다.
    if "Country" not in data.columns:
        data = data.rename(columns={data.columns[0]: "Country"})

    for mbti in MBTI_TYPES:
        if mbti in data.columns:
            data[mbti] = pd.to_numeric(data[mbti], errors="coerce")

    return data


# 파일 확인
if not CSV_PATH.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write("프로젝트 최상위 폴더에 아래 파일을 넣어 주세요.")
    st.code("countriesMBTI_16types (6).csv")
    st.stop()

try:
    df = load_data(str(CSV_PATH))
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

# CSV에 실제로 존재하는 MBTI 유형만 선택지로 표시
available_types = [
    mbti for mbti in MBTI_TYPES
    if mbti in df.columns
]

if not available_types:
    st.error("CSV 파일에서 MBTI 유형 열을 찾지 못했습니다.")
    st.write("현재 열 이름:", list(df.columns))
    st.stop()

# MBTI 선택
selected_mbti = st.selectbox(
    "🧠 분석할 MBTI를 선택하세요",
    available_types
)

# 선택한 MBTI의 국가별 데이터 정리
chart_df = df[["Country", selected_mbti]].copy()
chart_df["Country"] = chart_df["Country"].astype(str).str.strip()
chart_df[selected_mbti] = pd.to_numeric(
    chart_df[selected_mbti], errors="coerce"
)

chart_df = chart_df.dropna(subset=[selected_mbti])
chart_df = chart_df[chart_df["Country"] != ""]
chart_df = chart_df.drop_duplicates(subset=["Country"])

if chart_df.empty:
    st.warning("표시할 데이터가 없습니다.")
    st.stop()

# 데이터가 0~1이면 백분율로 변환
if chart_df[selected_mbti].max() <= 1:
    chart_df["비율(%)"] = chart_df[selected_mbti] * 100
else:
    chart_df["비율(%)"] = chart_df[selected_mbti]

chart_df["비율(%)"] = chart_df["비율(%)"].round(2)

# 높은 비율부터 낮은 비율 순으로 정렬
chart_df = chart_df.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)

chart_df["순위"] = range(1, len(chart_df) + 1)

# 색상 설정
purple_colors = [
    "#542078", "#65308A", "#764199", "#8752A8",
    "#9863B7", "#A974C6", "#BA85D5", "#CB96E3",
    "#D8A9EB", "#E5BDF2", "#F0D1F7"
]

color_map = {}
total = len(chart_df)

for i, country in enumerate(chart_df["Country"]):
    if total == 1:
        color_map[country] = "#FFD43B"
    elif i == 0:
        # 비율이 가장 높은 나라
        color_map[country] = "#FFD43B"
    elif i == total - 1:
        # 비율이 가장 낮은 나라
        color_map[country] = "#542078"
    else:
        # 중간 순위는 보라색 계열
        palette_index = round(
            (i - 1) / max(total - 2, 1)
            * (len(purple_colors) - 1)
        )
        color_map[country] = purple_colors[palette_index]

# 그래프는 아래에서 위로 낮은 값부터 그려야
# 화면에서는 높은 나라가 위쪽에 표시됩니다.
plot_df = chart_df.sort_values("비율(%)", ascending=True)

fig = px.bar(
    plot_df,
    x="비율(%)",
    y="Country",
    orientation="h",
    color="Country",
    color_discrete_map=color_map,
    text="비율(%)",
    hover_data={
        "Country": True,
        "비율(%)": ":.2f",
        "순위": True
    },
    title=f"📊 {selected_mbti} 비율이 높은 나라 TOP 비교",
    labels={
        "Country": "나라",
        "비율(%)": "비율 (%)"
    }
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    showlegend=False,
    xaxis_title="MBTI 비율 (%)",
    yaxis_title="나라",
    height=max(500, min(1600, len(chart_df) * 28)),
    margin=dict(l=20, r=70, t=70, b=30)
)

fig.update_yaxes(
    categoryorder="array",
    categoryarray=plot_df["Country"].tolist()
)

st.plotly_chart(fig, use_container_width=True)

# 최고·최저 국가 표시
highest = chart_df.iloc[0]
lowest = chart_df.iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label=f"🟡 {selected_mbti} 비율이 가장 높은 나라",
        value=str(highest["Country"]),
        delta=f"{highest
