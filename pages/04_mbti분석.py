
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# 1. 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="세계 MBTI 국가별 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 MBTI 국가별 비율 분석")
st.write("국가를 선택하면 MBTI 16개 유형의 비율을 그래프로 확인할 수 있어요!")


# -----------------------------
# 2. CSV 파일 경로 설정
# -----------------------------
# 현재 파이썬 파일은 pages 폴더에 있고,
# CSV 파일은 그 상위 폴더에 있습니다.
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "countriesMBTI_16types(6).csv"


# -----------------------------
# 3. CSV 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    # 열 이름의 앞뒤 공백 제거
    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    # 국가 이름이 없는 행 제거
    data = data.dropna(subset=["Country"]).copy()
    data["Country"] = data["Country"].astype(str).str.strip()

    # Country를 제외한 나머지 열을 MBTI 유형으로 설정
    mbti_types = [
        column for column in data.columns
        if column != "Country"
    ]

    if not mbti_types:
        raise ValueError("MBTI 유형 열을 찾을 수 없습니다.")

    # MBTI 데이터를 숫자로 변환
    for column in mbti_types:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    # 중복 국가 제거 및 국가 이름순 정렬
    data = data.drop_duplicates(subset=["Country"])
    data = data.sort_values("Country").reset_index(drop=True)

    return data, mbti_types


try:
    df, mbti_types = load_data(CSV_PATH)

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다.\n\n"
        f"확인한 경로: {CSV_PATH}\n\n"
        "CSV 파일이 app.py와 같은 상위 폴더에 있는지 "
        "확인해 주세요."
    )
    st.stop()

except (ValueError, pd.errors.ParserError) as error:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {error}")
    st.stop()


if df.empty:
    st.error("분석할 국가 데이터가 없습니다.")
    st.stop()


# -----------------------------
# 4. 국가 선택
# -----------------------------
countries = df["Country"].tolist()

# South Korea가 있으면 기본 선택
if "South Korea" in countries:
    default_index = countries.index("South Korea")
else:
    default_index = 0

selected_country = st.selectbox(
    "🌐 국가를 선택하세요",
    options=countries,
    index=default_index
)


# -----------------------------
# 5. 선택한 국가의 MBTI 데이터 정리
# -----------------------------
country_row = df.loc[
    df["Country"] == selected_country
].iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [
        country_row[mbti]
        for mbti in mbti_types
    ]
})

# 숫자로 변환할 수 없는 값 제거
chart_data["비율"] = pd.to_numeric(
    chart_data["비율"],
    errors="coerce"
)

chart_data = chart_data.dropna(
    subset=["비율"]
).copy()

if chart_data.empty:
    st.warning("선택한 국가에 표시할 MBTI 데이터가 없습니다.")
    st.stop()

# 비율을 백분율로 변환
chart_data["비율(%)"] = chart_data["비율"] * 100

# 높은 비율부터 정렬
chart_data = chart_data.sort_values(
    "비율(%)",
    ascending=False
).reset_index(drop=True)


# -----------------------------
# 6. 그래프 색상 설정
# -----------------------------
# 1위: 노란색
# 2위부터: 진한 보라색에서 연한 보라색
purple_gradient = [
    "#5B21B6",
    "#6D28D9",
    "#7C3AED",
    "#8B5CF6",
    "#9F7AEA",
    "#B09AF0",
    "#C4B5FD",
    "#D0C4FC",
    "#D9D0FD",
    "#E2DAFE",
    "#E8E1FE",
    "#EEE9FF",
    "#F1EDFF",
    "#F4F1FF",
    "#F7F5FF"
]

colors = ["#FFD43B"] + purple_gradient[
    :len(chart_data) - 1
]

# MBTI별 색상 지정
color_map = {
    mbti: colors[index]
    for index, mbti in enumerate(chart_data["MBTI"])
}


# -----------------------------
# 7. Plotly 막대그래프 만들기
# -----------------------------
st.divider()

st.subheader(
    f"📊 {selected_country}의 MBTI 비율"
)

st.caption(
    "🥇 1위는 노란색, "
    "나머지는 진한 보라색에서 연한 보라색으로 표시됩니다."
)

fig = px.bar(
    chart_data,
    x="비율(%)",
    y="MBTI",
    orientation="h",
    text="비율(%)",
    color="MBTI",
    color_discrete_map=color_map,
    category_orders={
        "MBTI": chart_data["MBTI"].tolist()[::-1]
    },
    labels={
        "비율(%)": "비율 (%)",
        "MBTI": "MBTI 유형"
    },
    title=f"{selected_country} - MBTI 유형별 비율"
)

# 막대 위에 비율 표시
fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>"
        "비율: %{x:.2f}%"
        "<extra></extra>"
    )
)

# 그래프 디자인
fig.update_layout(
    showlegend=False,
    height=650,
    margin=dict(
        l=20,
        r=80,
        t=70,
        b=50
    ),
    xaxis=dict(
        title="비율 (%)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)"
    ),
    yaxis=dict(
        title="",
        categoryorder="array",
        categoryarray=chart_data["MBTI"].tolist()[::-1]
    )
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------
# 8. 가장 높은 MBTI 결과
# -----------------------------
top_mbti = chart_data.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="🏆 비율 1위 MBTI",
        value=top_mbti["MBTI"]
    )

with col2:
    st.metric(
        label="📈 1위 비율",
        value=f"{top_mbti['비율(%)']:.2f}%"
    )


# -----------------------------
# 9. 상세 비율 표
# -----------------------------
with st.expander("📋 MBTI별 상세 비율 확인하기"):
    display_data = chart_data[
        ["MBTI", "비율(%)"]
    ].copy()

    display_data.columns = [
        "MBTI 유형",
        "비율(%)"
    ]

    st.dataframe(
        display_data.style.format({
            "비율(%)": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# 10. 데이터 안내
# -----------------------------
st.divider()

st.caption(
    "※ 비율은 제공된 CSV 데이터를 백분율로 변환한 값입니다. "
    "데이터가 각 국가 전체 인구를 대표하는지는 원본 출처를 확인해 주세요."
)
