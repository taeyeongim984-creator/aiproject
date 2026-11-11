
import re
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# -----------------------------------
# 1. 페이지 설정
# -----------------------------------
st.set_page_config(
    page_title="서울시 연령대별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 서울시 연령대별 인구 분석")
st.write(
    "행정구역과 연도를 선택하면 연령대별 인구를 "
    "노란색 꺾은선 그래프로 확인할 수 있습니다."
)


# -----------------------------------
# 2. CSV 파일 불러오기
# -----------------------------------
@st.cache_data
def load_data():
    # 현재 파일은 pages 폴더 안에 있고
    # CSV 파일은 그 상위 폴더에 있음
    project_folder = Path(__file__).resolve().parent.parent
    file_path = project_folder / "population (4).csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"CSV 파일을 찾을 수 없습니다.\n경로: {file_path}"
        )

    encodings = ["cp949", "utf-8-sig", "euc-kr"]
    data = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                file_path,
                encoding=encoding,
                thousands=","
            )
            break
        except UnicodeDecodeError:
            continue

    if data is None:
        raise ValueError(
            "CSV 인코딩을 확인해 주세요."
        )

    data.columns = data.columns.str.strip()

    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------------
# 3. 행정구역 이름 정리
# -----------------------------------
if "행정구역" not in df.columns:
    st.error(
        "'행정구역' 열이 없습니다. CSV의 열 이름을 확인해 주세요."
    )
    st.stop()


def get_district_name(value):
    name = re.sub(r"\s*\([^)]*\)\s*$", "", str(value))
    return name.strip()


df["행정구역명"] = df["행정구역"].apply(get_district_name)


# -----------------------------------
# 4. 연도 및 연령대별 열 찾기
# -----------------------------------
year_pattern = re.compile(r"^(\d{4})년_거주자_")

years = sorted({
    int(match.group(1))
    for column in df.columns
    if (match := year_pattern.match(column))
})

if not years:
    st.error(
        "연도별 인구 데이터를 찾을 수 없습니다. CSV 열 이름을 확인해 주세요."
    )
    st.stop()


age_pattern = re.compile(
    r"^\d{4}년_거주자_(\d+~\d+세|\d+세 이상)$"
)

age_columns = {}

for year in years:
    columns_for_year = []

    for column in df.columns:
        match = age_pattern.match(column)

        if match and column.startswith(f"{year}년_"):
            age_label = match.group(1)
            columns_for_year.append((age_label, column))

    def age_sort_key(item):
        label = item[0]
        return int(re.match(r"\d+", label).group())

    columns_for_year.sort(key=age_sort_key)
    age_columns[year] = columns_for_year


# -----------------------------------
# 5. 행정구역 및 연도 선택
# -----------------------------------
st.subheader("🔎 분석 조건 선택")

col1, col2 = st.columns(2)

district_options = df["행정구역명"].tolist()

with col1:
    selected_district = st.selectbox(
        "행정구역 선택",
        district_options,
        index=0
    )

with col2:
    selected_year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1,
        format_func=lambda year: f"{year}년"
    )


# -----------------------------------
# 6. 선택한 데이터 가져오기
# -----------------------------------
selected_rows = df[
    df["행정구역명"] == selected_district
]

if selected_rows.empty:
    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

selected_row = selected_rows.iloc[0]
selected_age_columns = age_columns.get(selected_year, [])

if not selected_age_columns:
    st.error(
        f"{selected_year}년의 연령대별 인구 열을 찾을 수 없습니다."
    )
    st.stop()


chart_data = []

for age_label, column in selected_age_columns:
    population = pd.to_numeric(
        selected_row[column],
        errors="coerce"
    )

    if pd.notna(population):
        chart_data.append({
            "나이": age_label,
            "인구수": int(population)
        })

age_df = pd.DataFrame(chart_data)

if age_df.empty:
    st.warning("그래프로 표시할 데이터가 없습니다.")
    st.stop()


# -----------------------------------
# 7. 총인구 표시
# -----------------------------------
total_column = f"{selected_year}년_거주자_총인구수"

if total_column in df.columns:
    total_population = pd.to_numeric(
        selected_row[total_column],
        errors="coerce"
    )
else:
    total_population = age_df["인구수"].sum()


metric1, metric2 = st.columns(2)

with metric1:
    st.metric(
        "선택한 행정구역",
        selected_district
    )

with metric2:
    if pd.notna(total_population):
        st.metric(
            f"{selected_year}년 총인구",
            f"{int(total_population):,}명"
        )
    else:
        st.metric(
            f"{selected_year}년 총인구",
            "자료 없음"
        )


# -----------------------------------
# 8. 노란색 꺾은선 그래프
# -----------------------------------
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=age_df["나이"],
        y=age_df["인구수"],
        mode="lines+markers",
        name="인구수",
        line=dict(
            color="#FFD700",
            width=4
        ),
        marker=dict(
            color="#FFD700",
            size=9,
            line=dict(
                color="#B8860B",
                width=1
            )
        ),
        hovertemplate=(
            "연령대: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)

max_population = int(age_df["인구수"].max())

y_axis_max = max(
    1000,
    ((max_population + 999) // 1000) * 1000
)

fig.update_layout(
    title=f"{selected_district} {selected_year}년 연령대별 인구",
    xaxis_title="나이",
    yaxis_title="인구수 (명)",
    template="plotly_white",
    height=550,
    hovermode="x unified",
    margin=dict(
        l=30,
        r=30,
        t=70,
        b=30
    ),
    xaxis=dict(
        type="category",
        showgrid=False,
        tickangle=0
    ),
    yaxis=dict(
        range=[0, y_axis_max],
        tickmode="linear",
        tick0=0,
        dtick=1000,
        tickformat=",",
        showgrid=True,
        gridcolor="#D9D9D9",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="#888888"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -----------------------------------
# 9. 연령대별 인구 표
# -----------------------------------
with st.expander("📋 연령대별 인구 데이터 보기"):
    display_df = age_df.copy()

    display_df["인구수"] = display_df["인구수"].map(
        lambda value: f"{value:,}명"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------------
# 10. 자료 안내
# -----------------------------------
st.caption(
    "자료: population (4).csv | 인구수 단위: 명"
)

