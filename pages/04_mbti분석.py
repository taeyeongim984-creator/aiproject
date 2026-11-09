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
st.write("MBTI를 선택하면 비율이 높은 나라와 낮은 나라를 비교할 수 있어요!")

# CSV 파일 위치
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "countriesMBTI_16types (6).csv"

MBTI_TYPES = [
    "INFJ", "ISFJ", "INTP", "ISFP",
    "ENTP", "INFP", "ENTJ", "ISTP",
    "INTJ", "ESFP", "ESTJ", "ENFP",
    "ESTP", "ISTJ", "ENFJ", "ESFJ"
]


@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        data = data.rename(
            columns={data.columns[0]: "Country"}
        )

    for mbti in MBTI_TYPES:
        if mbti in data.columns:
            data[mbti] = pd.to_numeric(
                data[mbti], errors="coerce"
            )

    return data


# CSV 파일 확인
if not CSV_PATH.exists():
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.write(
        "countriesMBTI_16types (6).csv 파일을 "
        "프로젝트 최상위 폴더에 넣어 주세요."
    )
    st.stop()


try:
    df = load_data(str(CSV_PATH))
except Exception as error:
    st.error("CSV 파일을 읽는 중 오류가 발생했습니다.")
    st.code(str(error))
    st.stop()


# 사용 가능한 MBTI 유형 확인
available_types = [
    mbti for mbti in MBTI_TYPES
    if mbti in df.columns
]

if not available_types:
    st.error("CSV 파일에서 MBTI 열을 찾지 못했습니다.")
    st.write("CSV 열 이름:", list(df.columns))
    st.stop()


# MBTI 선택
selected_mbti = st.selectbox(
    "🧠 MBTI 유형 선택",
    available_types
)


# 선택한 유형의 국가별 데이터 추출
chart_df = df[["Country", selected_mbti]].copy()

chart_df["Country"] = (
    chart_df["Country"].astype(str).str.strip()
)

chart_df[selected_mbti] = pd.to_numeric(
    chart_df[selected_mbti],
    errors="coerce"
)

chart_df = chart_df.dropna(
    subset=[selected_mbti]
)

chart_df = chart_df[
    chart_df["Country"] != ""
]

chart_df = chart_df.drop_duplicates(
    subset=["Country"]
)

if chart_df.empty:
    st.warning("표시할 데이터가 없습니다.")
    st.stop()


# 비율 데이터가 0~1이면 백분율로 변환
if chart_df[selected_mbti].max() <= 1:
    chart_df["비율(%)"] = (
        chart_df[selected_mbti] * 100
    )
else:
    chart_df["비율(%)"] = chart_df[selected_mbti]

chart_df["비율(%)"] = chart_df["비율(%)"].round(2)


# 높은 비율부터 정렬
chart_df = chart_df.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)

chart_df["순위"] = range(1, len(chart_df) + 1)


# 색상 설정
# 가장 높은 나라: 노란색
# 가장 낮은 나라: 진한 보라색
# 나머지 나라: 보라색 계열
purple_colors = [
    "#542078",
    "#65308A",
    "#764199",
    "#8752A8",
    "#9863B7",
    "#A974C6",
    "#BA85D5",
    "#CB96E3",
    "#D8A9EB",
    "#E5BDF2",
    "#F0D1F7"
]

color_map = {}
total = len(chart_df)

for i, country in enumerate(chart_df["Country"]):
    if total == 1:
        color_map[country] = "#FFD43B"
    elif i == 0:
        color_map[country] = "#FFD43B"
    elif i == total - 1:
        color_map[country] = "#542078"
    else:
        palette_index = int(
            (i - 1) / max(total - 2, 1)
            * (len(purple_colors) - 1)
        )

        palette_index = min(
            palette_index,
            len(purple_colors) - 1
        )

        color_map[country] = purple_colors[palette_index]


# 가로 막대그래프
# 그래프에서 높은 비율이 위쪽에 표시되도록 정렬
plot_df = chart_df.sort_values(
    "비율(%)",
    ascending=True
)

fig = px.bar(
    plot_df,
    x="비율(%)",
    y="Country",
    orientation="h",
    color="Country",
    color_discrete_map=color_map,
    text="비율(%)",
    hover_data=["순위"],
    labels={
        "Country": "나라",
        "비율(%)": "비율 (%)"
    },
    title=f"{selected_mbti} 국가별 비율"
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    showlegend=False,
    xaxis_title="비율 (%)",
    yaxis_title="나라",
    height=max(
        500,
        min(1600, len(chart_df) * 28)
    ),
    margin=dict(
        l=20,
        r=70,
        t=70,
        b=30
    )
)

fig.update_yaxes(
    categoryorder="array",
    categoryarray=plot_df["Country"].tolist()
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# 가장 높은 나라와 가장 낮은 나라
highest = chart_df.iloc[0]
lowest = chart_df.iloc[-1]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="🟡 비율이 가장 높은 나라",
        value=str(highest["Country"]),
        delta=f'{highest["비율(%)"]:.2f}%'
    )

with col2:
    st.metric(
        label="🟣 비율이 가장 낮은 나라",
        value=str(lowest["Country"]),
        delta=f'{lowest["비율(%)"]:.2f}%'
    )


# 모든 나라의 비율 표
with st.expander("📋 모든 나라의 비율 보기"):
    display_df = chart_df[
        ["순위", "Country", "비율(%)"]
    ].rename(
        columns={"Country": "나라"}
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
