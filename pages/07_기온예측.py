
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="월별 평균기온 예측 AI",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 AI")
st.write(
    "과거 기온 데이터를 이용해 선형회귀 알고리즘으로 "
    "선택한 연도의 평균기온을 예측합니다."
)

# --------------------------------------------------
# 2. CSV 파일 불러오기
# temperature.csv는 app.py와 같은 폴더에 있어야 합니다.
# --------------------------------------------------
@st.cache_data
def load_data():
    file_path = Path(__file__).resolve().parent / "temperature.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            "temperature.csv 파일을 app.py와 같은 폴더에 넣어주세요."
        )

    # 한글 CSV의 인코딩을 고려하여 파일 읽기
    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다."
            )

    # 날짜와 평균기온 정리
    data["일시"] = pd.to_datetime(
        data["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["일시", "평균기온(℃)"]
    ).copy()

    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    return data.sort_values("일시")


try:
    df = load_data()
except Exception as error:
    st.error(f"데이터를 불러오지 못했습니다: {error}")
    st.stop()

if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()

# --------------------------------------------------
# 3. 월과 예측 연도 선택
# --------------------------------------------------
st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda month: f"{month}월",
        index=0
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 입력하세요",
        min_value=1900,
        max_value=2100,
        value=int(df["연도"].max()) + 1,
        step=1
    )

selected_year = int(selected_year)

# 선택한 월의 모든 연도별 데이터 추출
month_data = df[df["월"] == selected_month].copy()
month_data = month_data.sort_values("연도")

if len(month_data) < 2:
    st.warning(
        f"{selected_month}월의 데이터가 부족해 "
        "선형회귀를 계산할 수 없습니다."
    )
    st.stop()

# --------------------------------------------------
# 4. 선형회귀 알고리즘
# X: 연도, Y: 평균기온
# --------------------------------------------------
X = month_data["연도"].to_numpy(dtype=float)
Y = month_data["평균기온(℃)"].to_numpy(dtype=float)

# y = a*x + b 형태의 직선 계산
slope, intercept = np.polyfit(X, Y, 1)

# 각 과거 연도의 회귀 예측값
fitted_values = slope * X + intercept

# 사용자가 입력한 연도의 예측 기온
predicted_temperature = slope * selected_year + intercept

# 결정계수 R² 계산
ss_res = np.sum((Y - fitted_values) ** 2)
ss_tot = np.sum((Y - np.mean(Y)) ** 2)

if ss_tot == 0:
    r_squared = 0.0
else:
    r_squared = 1 - (ss_res / ss_tot)

# --------------------------------------------------
# 5. 예측 결과 표시
# --------------------------------------------------
st.subheader("🔮 기온 예측 결과")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric(
        label=f"{selected_year}년 {selected_month}월 예측 평균기온",
        value=f"{predicted_temperature:.1f} °C"
    )

with result_col2:
    st.metric(
        label="회귀 직선의 기울기",
        value=f"{slope:.3f} °C/년"
    )

with result_col3:
    st.metric(
        label="결정계수 (R²)",
        value=f"{r_squared:.3f}"
    )

st.caption(
    "예측값은 선택한 월의 과거 평균기온을 이용한 통계적 추정치입니다. "
    "실제 관측 기온과 다를 수 있습니다."
)

# --------------------------------------------------
# 6. 그래프 시각화
# --------------------------------------------------
st.subheader(f"📈 {selected_month}월 평균기온 및 선형회귀 예측")

# 한글 글꼴 설정
plt.rcParams["font.family"] = [
    "Malgun Gothic",
    "AppleGothic",
    "DejaVu Sans"
]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 6))

# 실제로 관측한 평균기온: 파란색 점
ax.scatter(
    X,
    Y,
    color="royalblue",
    s=55,
    label="실제 평균기온",
    zorder=4
)

# 회귀선이 계산한 과거 기온: 실제 데이터 범위에서 실선
historical_line_x = np.linspace(X.min(), X.max(), 200)
historical_line_y = slope * historical_line_x + intercept

ax.plot(
    historical_line_x,
    historical_line_y,
    color="darkorange",
    linewidth=2.5,
    label="선형회귀 추세선",
    zorder=2
)

# 각 관측값과 회귀선 사이의 차이(잔차)를 세로선으로 표시
for year, actual, fitted in zip(X, Y, fitted_values):
    ax.plot(
        [year, year],
        [actual, fitted],
        color="gray",
        alpha=0.35,
        linewidth=0.8,
        zorder=1
    )

# 예측 연도가 과거 데이터 범위를 벗어나면 외삽 구간을 점선으로 표시
if selected_year > X.max():
    extension_x = np.linspace(X.max(), selected_year, 100)
    extension_y = slope * extension_x + intercept

    ax.plot(
        extension_x,
        extension_y,
        color="darkorange",
        linestyle="--",
        linewidth=2.5,
        label="미래 예측 구간"
    )

elif selected_year < X.min():
    extension_x = np.linspace(selected_year, X.min(), 100)
    extension_y = slope * extension_x + intercept

    ax.plot(
        extension_x,
        extension_y,
        color="darkorange",
        linestyle="--",
        linewidth=2.5,
        label="과거 방향 추정 구간"
    )

# 예측 기온: 빨간색 별표
ax.scatter(
    [selected_year],
    [predicted_temperature],
    color="crimson",
    marker="*",
    s=300,
    edgecolors="black",
    linewidths=0.7,
    label=f"{selected_year}년 예측 기온",
    zorder=5
)

# 예측값을 그래프에 직접 표시
ax.annotate(
    f"{predicted_temperature:.1f}°C",
    xy=(selected_year, predicted_temperature),
    xytext=(8, 12),
    textcoords="offset points",
    color="crimson",
    fontsize=11,
    fontweight="bold"
)

ax.set_title(
    f"{selected_month}월 평균기온 선형회귀 분석",
    fontsize=16
)
ax.set_xlabel("연도", fontsize=12)
ax.set_ylabel("평균기온 (℃)", fontsize=12)

ax.grid(True, linestyle=":", alpha=0.5)
ax.legend(loc="best")
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# --------------------------------------------------
# 7. 과거 데이터 표
# --------------------------------------------------
with st.expander("📋 선택한 월의 전체 기온 데이터 보기"):
    display_data = month_data[["연도", "일시", "평균기온(℃)"]].copy()
    display_data["일시"] = display_data["일시"].dt.strftime("%Y년 %m월")

    st.dataframe(
        display_data.rename(
            columns={
                "연도": "연도",
                "일시": "관측 월",
                "평균기온(℃)": "평균기온(℃)"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 8. 선형회귀 알고리즘 쉽게 설명하기
# --------------------------------------------------
st.divider()
st.subheader("🧠 선형회귀 알고리즘이란?")

st.markdown("""
선형회귀는 **과거 데이터의 전체적인 흐름을 가장 잘 나타내는 직선**을 찾고,
그 직선을 이용해 새로운 값을 예측하는 알고리즘입니다.

**① 파란색 점 — 실제 평균기온**
- CSV 파일에 기록된 각 연도의 실제 평균기온입니다.
- 점 하나가 특정 연도의 해당 월 평균기온을 의미합니다.

**② 주황색 실선 — 선형회귀 추세선**
- 과거의 모든 기온 데이터를 바탕으로 계산한 직선입니다.
- 실제 점들과 직선 사이의 세로 방향 차이를 전체적으로 작게 만드는 방향으로 직선을 결정합니다.
- 직선이 오른쪽으로 올라가면 장기적인 상승 경향, 내려가면 하락 경향을 뜻합니다.

**③ 회색 세로선 — 예측 오차(잔차)**
- 실제 기온과 회귀 직선이 계산한 기온의 차이입니다.
- 세로선이 짧을수록 해당 데이터의 실제값이 회귀선에 가깝다는 뜻입니다.

**④ 빨간색 별표 — 선택한 연도의 예측 기온**
- 계산한 회귀 직선에 사용자가 선택한 연도를 넣어 얻은 값입니다.
- 과거 데이터의 범위 바깥에 있는 연도를 예측하면 점선으로 표시된 구간까지 직선을 연장합니다.

### 선형회귀는 어떻게 계산할까요?

이 프로그램은 다음과 같은 직선의 식을 사용합니다.

**예측 평균기온 = 기울기 × 연도 + 절편**

- **기울기:** 연도가 1년 증가할 때 회귀선의 기온이 얼마나 변하는지를 나타냅니다.
- **절편:** 직선의 위치를 결정하는 값입니다.
- **예측:** 선택한 연도를 식에 대입해 평균기온을 계산합니다.

선형회귀는 과거 데이터의 경향을 바탕으로 추정합니다. 계절별 기온 변화나 갑작스러운 기후 변화까지 반영하는 복잡한 기상예보 모델은 아니므로, 예측값을 실제 기온과 동일하다고 해석하면 안 됩니다.
""")

st.info(
    "💡 그래프를 읽는 핵심: 파란색 점은 실제 관측값, "
    "주황색 선은 데이터에서 학습한 직선, "
    "빨간색 별표는 선택한 연도의 예측값입니다."
)
