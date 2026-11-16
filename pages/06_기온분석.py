
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택해 연도별 최고기온과 최저기온을 비교하세요.")

# CSV 파일 경로
CSV_PATH = Path(__file__).parent / "temperature.csv"


@st.cache_data
def load_data(path):
    # CSV 인코딩 자동 확인
    df = None

    for encoding in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            df = pd.read_csv(path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 인코딩을 확인해 주세요. UTF-8 또는 CP949를 사용하세요."
        )

    # 필요한 열 확인
    required = ["일시", "최고기온(℃)", "최저기온(℃)"]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"CSV에 '{col}' 열이 없습니다.")

    # 날짜 변환: Oct-07 → 2007년 10월
    df["일시"] = df["일시"].astype(str).str.strip()
    df["날짜"] = pd.to_datetime(
        df["일시"],
        format="%b-%y",
        errors="coerce"
    )

    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 기온을 숫자로 변환
    df["최고기온(℃)"] = pd.to_numeric(
        df["최고기온(℃)"], errors="coerce"
    )
    df["최저기온(℃)"] = pd.to_numeric(
        df["최저기온(℃)"], errors="coerce"
    )

    df = df.dropna(subset=["날짜", "연도", "월"])
    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df.sort_values("날짜")


# 데이터 불러오기
if not CSV_PATH.exists():
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 CSV 파일을 넣어 주세요."
    )
    st.stop()

try:
    df = load_data(CSV_PATH)
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# 월 선택 버튼
months = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월",
    5: "5월", 6: "6월", 7: "7월", 8: "8월",
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

selected_label = st.selectbox(
    "📅 분석할 월 선택",
    list(months.values())
)

selected_month = next(
    month for month, label in months.items()
    if label == selected_label
)

# 선택한 월의 데이터만 추출
monthly = df[df["월"] == selected_month].sort_values("연도")

if monthly.empty:
    st.warning("선택한 월의 데이터가 없습니다.")

else:
    # 꺾은선 그래프
    fig = go.Figure()

    # 최고기온: 핫노랑
    fig.add_trace(go.Scatter(
        x=monthly["연도"],
        y=monthly["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="#FFD400", width=3),
        marker=dict(size=7)
    ))

    # 최저기온: 하늘색
    fig.add_trace(go.Scatter(
        x=monthly["연도"],
        y=monthly["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="#87CEEB", width=3),
        marker=dict(size=7)
    ))

    # 제목, 축, 범례 설정
    fig.update_layout(
        title="월별 기온분석",
        xaxis_title="연도",
        yaxis_title="온도(℃)",
        legend_title="기온 구분",
        hovermode="x unified",
        template="plotly_white",
        xaxis=dict(dtick=1, tickformat="d"),
        margin=dict(l=20, r=20, t=70, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"선택한 월: {selected_label} | "
        "각 점은 해당 연도의 기온 자료입니다."
    )

    # 그래프에 사용된 데이터 확인
    with st.expander("📋 그래프 데이터 확인"):
        st.dataframe(
            monthly[["연도", "최고기온(℃)", "최저기온(℃)"]],
            use_container_width=True,
            hide_index=True
        )
