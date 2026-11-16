
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교하세요.")

# ---------------------------------
# 2. CSV 파일 경로 설정
# app.py는 pages 폴더 안에 있고,
# CSV는 그 상위 폴더에 있음
# ---------------------------------
CSV_PATH = Path(__file__).resolve().parent.parent / "temperature.csv"


# ---------------------------------
# 3. 데이터 불러오기 및 전처리
# ---------------------------------
@st.cache_data
def load_data(file_path):
    # 한글 인코딩 확인
    df = None

    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 인코딩을 확인해 주세요. UTF-8 또는 CP949가 필요합니다."
        )

    # 열 이름 양쪽 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 필요한 열 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
            + "\n실제 열 이름: "
            + ", ".join(df.columns)
        )

    # 날짜 형식 예: Jan-63, Oct-07
    df["일시"] = df["일시"].astype(str).str.strip()

    df["날짜"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    # 날짜가 미래 연도로 잘못 해석된 경우
    # 2063년 → 1963년처럼 100년을 조정
    future_year = df["날짜"].dt.year > pd.Timestamp.today().year

    df.loc[future_year, "날짜"] = (
        df.loc[future_year, "날짜"]
        - pd.DateOffset(years=100)
    )

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온 열을 숫자로 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"], errors="coerce"
    )

    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"], errors="coerce"
    )

    # 날짜가 없는 행 제외
    df = df.dropna(subset=["날짜", "연도", "월"])

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df.sort_values("날짜")


# ---------------------------------
# 4. 데이터 불러오기
# ---------------------------------
if not CSV_PATH.exists():
    st.error(
        f"CSV 파일을 찾을 수 없습니다.\n\n"
        f"찾는 경로: {CSV_PATH}\n\n"
        "temperature.csv 파일이 프로젝트 상위 폴더에 있는지 확인하세요."
    )
    st.stop()

try:
    df = load_data(CSV_PATH)
except Exception as e:
    st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
    st.stop()


# ---------------------------------
# 5. 월 선택
# ---------------------------------
month_names = {
    1: "1월",
    2: "2월",
    3: "3월",
    4: "4월",
    5: "5월",
    6: "6월",
    7: "7월",
    8: "8월",
    9: "9월",
    10: "10월",
    11: "11월",
    12: "12월"
}

selected_month_name = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    list(month_names.values())
)

selected_month = next(
    month
    for month, name in month_names.items()
    if name == selected_month_name
)


# ---------------------------------
# 6. 선택한 월의 데이터 추출
# ---------------------------------
monthly_data = df[
    df["월"] == selected_month
].copy()

# 같은 연도에 자료가 여러 개 있다면 연도별 평균 계산
monthly_data = (
    monthly_data
    .groupby("연도", as_index=False)[
        ["최고기온(℃)", "최저기온(℃)"]
    ]
    .mean()
    .sort_values("연도")
)


# ---------------------------------
# 7. 꺾은선 그래프
# ---------------------------------
if monthly_data.empty:
    st.warning("선택한 월에 해당하는 데이터가 없습니다.")

else:
    fig = go.Figure()

    # 최고기온: 핫노랑
    fig.add_trace(
        go.Scatter(
            x=monthly_data["연도"],
            y=monthly_data["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FFD400",
                width=3
            ),
            marker=dict(size=7),
            connectgaps=False
        )
    )

    # 최저기온: 하늘색
    fig.add_trace(
        go.Scatter(
            x=monthly_data["연도"],
            y=monthly_data["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(size=7),
            connectgaps=False
        )
    )

    # 그래프 제목과 축
    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="연도",
        yaxis_title="온도(℃)",
        legend_title="범례",
        hovermode="x unified",
        template="plotly_white",
        xaxis=dict(
            type="linear",
            tickformat="d",
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,
            zeroline=True
        ),
        margin=dict(
            l=30,
            r=30,
            t=80,
            b=40
        )
    )

    st.subheader(f"📈 {selected_month_name} 기온 그래프")
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------
    # 8. 그래프 데이터 표
    # ---------------------------------
    with st.expander("📋 그래프 데이터 확인"):
        display_data = monthly_data.rename(
            columns={
                "연도": "연도",
                "최고기온(℃)": "최고기온(℃)",
                "최저기온(℃)": "최저기온(℃)"
            }
        )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        f"분석 월: {selected_month_name} | "
        f"데이터 연도 범위: "
        f"{monthly_data['연도'].min()}년 ~ "
        f"{monthly_data['연도'].max()}년"
    )

# 비교할 연도 2개 선택
available_years = sorted(df["연도"].dropna().unique().tolist())

if len(available_years) < 2:
    st.warning("비교할 수 있는 연도가 2개 이상 필요합니다.")
    st.stop()

year1, year2 = st.selectbox(
    "📅 비교할 첫 번째 연도",
    available_years,
    index=0
), st.selectbox(
    "📅 비교할 두 번째 연도",
    available_years,
    index=len(available_years) - 1
)

if year1 == year2:
    st.warning("서로 다른 연도를 선택해 주세요.")
    st.stop()
