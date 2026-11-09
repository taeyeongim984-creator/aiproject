from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="세계 MBTI 국가별 분석",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 세계 MBTI 국가별 비율 분석")
st.write("국가를 선택하면 해당 국가의 MBTI 16개 유형 비율을 막대그래프로 확인할 수 있어요.")

# app.py와 CSV 파일을 같은 GitHub 저장소 폴더에 업로드하세요.
CSV_PATH = Path(__file__).parent / "countriesMBTI_16types (6).csv"


@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 'Country' 열이 없습니다.")

    data = data.dropna(subset=["Country"]).copy()
    data["Country"] = data["Country"].astype(str).str.strip()

    mbti_types = [column for column in data.columns if column != "Country"]
    if not mbti_types:
        raise ValueError("MBTI 유형 열을 찾을 수 없습니다.")

    for column in mbti_types:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.drop_duplicates(subset=["Country"])
    data = data.sort_values("Country").reset_index(drop=True)
    return data, mbti_types


try:
    df, mbti_types = load_data(CSV_PATH)
except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. GitHub 저장소에서 "
        "'app.py'와 'countriesMBTI_16types (6).csv'를 같은 폴더에 넣어 주세요."
    )
    st.stop()
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
    st.stop()

if df.empty:
    st.error("분석할 국가 데이터가 없습니다.")
    st.stop()

countries = df["Country"].tolist()
default_index = countries.index("South Korea") if "South Korea" in countries else 0

selected_country = st.selectbox(
    "🌐 국가 선택",
    options=countries,
    index=default_index,
)

country_row = df.loc[df["Country"] == selected_country].iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [country_row[mbti] for mbti in mbti_types],
})
chart_data["비율"] = pd.to_numeric(chart_data["비율"], errors="coerce")
chart_data = chart_data.dropna(subset=["비율"]).copy()

if chart_data.empty:
    st.warning("선택한 국가에 표시할 MBTI 비율 데이터가 없습니다.")
    st.stop()

# CSV의 값은 0~1 비율이므로 백분율로 변환합니다.
chart_data["비율(%)"] = chart_data["비율"] * 100
chart_data = chart_data.sort_values(
    "비율(%)", ascending=False
).reset_index(drop=True)

# 1위는 노란색, 2위부터는 진한 보라색에서 연한 보라색으로 표시합니다.
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
    "#F7F5FF",
]

colors = ["#FFD43B"] + purple_gradient[: max(0, len(chart_data) - 1)]
color_map = {
    mbti: colors[index]
    for index, mbti in enumerate(chart_data["MBTI"])
}

st.subheader(f"📊 {selected_country}의 MBTI 비율")
st.caption("1위: 노란색 · 나머지: 진한 보라색에서 연한 보라색으로")

fig = px.bar(
    chart_data,
    x="비율(%)",
    y="MBTI",
    orientation="h",
    text="비율(%)",
    color="MBTI",
    color_discrete_map=color_map,
    category_orders={"MBTI": chart_data["MBTI"].tolist()[::-1]},
    labels={
        "비율(%)": "비율 (%)",
        "MBTI": "MBTI 유형",
    },
    title=f"{selected_country} — MBTI 유형별 비율",
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False,
    hovertemplate="<b>%{y}</b><br>비율: %{x:.2f}%<extra></extra>",
)

fig.update_layout(
    showlegend=False,
    height=650,
    margin=dict(l=20, r=70, t=70, b=40),
    xaxis=dict(
        title="비율 (%)",
        rangemode="tozero",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
    ),
    yaxis=dict(
        title="",
        categoryorder="array",
        categoryarray=chart_data["MBTI"].tolist()[::-1],
    ),
)

st.plotly_chart(fig, use_container_width=True)

top = chart_data.iloc[0]
col1, col2 = st.columns(2)
col1.metric("가장 높은 비율의 유형", str(top["MBTI"]))
col2.metric("1위 비율", f"{top['비율(%)']:.2f}%")

with st.expander("📋 비율 데이터 표 보기"):
    table = chart_data[["MBTI", "비율(%)"]].copy()
    st.dataframe(
        table.style.format({"비율(%)": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "참고: 이 그래프는 제공된 CSV의 수치를 백분율로 변환해 표시합니다. "
    "데이터가 각 국가 전체 인구를 대표하는지는 원본 출처를 확인하세요."
)
