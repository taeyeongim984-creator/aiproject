
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="월별 평균기온 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균기온 예측 프로그램")
st.write(
    "temperature.csv의 실제 기온 데이터를 이용해 "
    "선택한 월의 평균기온 추세를 확인하고 미래 기온을 예측합니다."
)

st.info("📌 실제 관측 데이터는 2025년까지 표시합니다.")

# --------------------------------------------------
# 2. CSV 파일 불러오기
# CSV 파일은 pages 폴더의 상위 폴더에 있음
# --------------------------------------------------
CSV_PATH = Path(__file__).resolve().parent.parent / "temperature.csv"

if not CSV_PATH.exists():
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다.\n\n"
        "프로젝트 최상위 폴더에 temperature.csv 파일이 있는지 확인해 주세요."
    )
    st.stop()

try:
    try:
        data = pd.read_csv(CSV_PATH, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

# --------------------------------------------------
# 3. 필요한 열 확인
# --------------------------------------------------
date_col = "일시"
temp_col = "평균기온(℃)"

if date_col not in data.columns:
    st.error(
        f"'{date_col}' 열을 찾을 수 없습니다.\n\n"
        f"CSV의 실제 열 이름: {list(data.columns)}"
    )
    st.stop()

if temp_col not in data.columns:
    st.error(
        f"'{temp_col}' 열을 찾을 수 없습니다.\n\n"
        f"CSV의 실제 열 이름: {list(data.columns)}"
    )
    st.stop()

# --------------------------------------------------
# 4. 날짜와 기온 데이터 정리
# --------------------------------------------------
date_text = data[date_col].astype(str).str.strip()

# 예: Oct-07 형식의 날짜 읽기
dates = pd.to_datetime(
    date_text,
    format="%b-%y",
    errors="coerce"
)

# 다른 날짜 형식도 읽을 수 있도록 추가 처리
missing_dates = dates.isna()

if missing_dates.any():
    dates.loc[missing_dates] = pd.to_datetime(
        date_text.loc[missing_dates],
        errors="coerce"
    )

data["날짜"] = dates

# 평균기온을 숫자로 변환
data["평균기온"] = pd.to_numeric(
    data[temp_col].astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("℃", "", regex=False)
    .str.strip(),
    errors="coerce"
)

# 날짜 또는 기온이 없는 행 제거
data = data.dropna(subset=["날짜", "평균기온"]).copy()

data["연도"] = data["날짜"].dt.year
data["월"] = data["날짜"].dt.month

# 실제 관측 데이터는 2025년까지 사용
data = data[data["연도"] <= 2025].copy()

if data.empty:
    st.error(
        "2025년까지의 유효한 기온 데이터가 없습니다. "
        "CSV의 날짜 형식과 열 이름을 확인해 주세요."
    )
    st.stop()

# --------------------------------------------------
# 5. 사용자 입력
# --------------------------------------------------
st.subheader("🔎 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요",
        list(range(1, 13)),
        index=0,
        format_func=lambda month: f"{month}월"
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도를 선택하세요",
        min_value=2026,
        max_value=2100,
        value=2026,
        step=1
    )

# 선택한 월의 자료만 사용
monthly_data = data[data["월"] == selected_month].copy()
monthly_data = monthly_data.sort_values("연도")

# 같은 연도에 데이터가 여러 개라면 연도별 평균으로 정리
monthly_data = (
    monthly_data.groupby("연도", as_index=False)["평균기온"]
    .mean()
)

if len(monthly_data) < 2:
    st.error(
        f"{selected_month}월의 유효한 데이터가 2개 연도 이상 있어야 "
        "선형회귀 예측을 할 수 있습니다."
    )
    st.stop()

# --------------------------------------------------
# 6. NumPy를 이용한 선형회귀
# y = 기울기 * 연도 + 절편
# --------------------------------------------------
years = monthly_data["연도"].to_numpy(dtype=float)
temperatures = monthly_data["평균기온"].to_numpy(dtype=float)

# 1차 직선의 기울기와 절편 계산
slope, intercept = np.polyfit(years, temperatures, 1)

# 실제 관측 연도의 추세선 기온
fitted_values = slope * years + intercept

# 사용자가 선택한 연도의 예측 기온
predicted_temperature = slope * selected_year + intercept

# 잔차 = 실제 기온 - 추세선 기온
residuals = temperatures - fitted_values

# 결정계수 R² 계산
total_variation = np.sum((temperatures - np.mean(temperatures)) ** 2)
residual_variation = np.sum(residuals ** 2)

if total_variation > 0:
    r_squared = 1 - residual_variation / total_variation
else:
    r_squared = 0.0

# --------------------------------------------------
# 7. 예측 결과 표시
# --------------------------------------------------
st.subheader("📊 기온 예측 결과")

result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric(
        label=f"{selected_year}년 {selected_month}월 예측 평균기온",
        value=f"{predicted_temperature:.2f} ℃"
    )

with result_col2:
    st.metric(
        label="연도별 기온 변화 추세",
        value=f"{slope:+.3f} ℃/년"
    )

with result_col3:
    st.metric(
        label="결정계수 R²",
        value=f"{r_squared:.3f}"
    )

if slope > 0:
    st.write(
        f"📈 분석된 추세에서는 {selected_month}월 평균기온이 "
        f"연평균 약 {slope:.3f}℃ 상승하는 경향을 보입니다."
    )
elif slope < 0:
    st.write(
        f"📉 분석된 추세에서는 {selected_month}월 평균기온이 "
        f"연평균 약 {abs(slope):.3f}℃ 하락하는 경향을 보입니다."
    )
else:
    st.write("➡️ 분석된 직선 추세에서는 평균기온의 변화가 거의 없습니다.")

st.caption(
    "주의: 예측값은 과거 자료에 직선을 맞춘 추정치이며, "
    "실제 미래 기온과 다를 수 있습니다."
)

# --------------------------------------------------
# 8. 그래프 그리기
# 실제 관측값은 2025년까지 표시
# 추세선은 선택한 예측 연도까지 연장
# --------------------------------------------------
st.subheader(f"📈 {selected_month}월 평균기온 그래프")

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 관측값
ax.scatter(
    years,
    temperatures,
    label="Actual temperature (through 2025)",
    marker="o"
)

ax.plot(
    years,
    temperatures,
    linestyle=":",
    alpha=0.55,
    label="Actual data connection"
)

# 추세선을 2025년 이후 예측 연도까지 연장
line_years = np.linspace(
    float(years.min()),
    max(float(selected_year), float(years.max())),
    300
)

line_temperatures = slope * line_years + intercept

ax.plot(
    line_years,
    line_temperatures,
    label="Linear regression trend"
)

# 실제값과 추세선 사이의 차이(잔차)를 수직선으로 표시
ax.vlines(
    years,
    np.minimum(temperatures, fitted_values),
    np.maximum(temperatures, fitted_values),
    linestyles="dashed",
    alpha=0.45,
    label="Residuals"
)

# 예측 지점 표시
ax.scatter(
    [selected_year],
    [predicted_temperature],
    marker="*",
    s=220,
    label=f"Prediction for {selected_year}"
)

ax.annotate(
    f"{predicted_temperature:.2f} °C",
    (selected_year, predicted_temperature),
    xytext=(8, 10),
    textcoords="offset points"
)

ax.set_title(f"Monthly Average Temperature: {selected_month} Month")
ax.set_xlabel("Year")
ax.set_ylabel("Average Temperature (°C)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# --------------------------------------------------
# 9. 실제 데이터와 추세선 값 비교
# --------------------------------------------------
st.subheader("🧾 실제 기온과 추세선 비교")

comparison = monthly_data.copy()
comparison["추세선 기온(℃)"] = fitted_values
comparison["잔차(℃)"] = residuals

comparison = comparison.rename(
    columns={
        "연도": "연도",
        "평균기온": "실제 평균기온(℃)"
    }
)

comparison["실제 평균기온(℃)"] = comparison[
    "실제 평균기온(℃)"
].round(2)

comparison["추세선 기온(℃)"] = comparison[
    "추세선 기온(℃)"
].round(2)

comparison["잔차(℃)"] = comparison["잔차(℃)"].round(2)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "잔차는 실제 평균기온에서 추세선 기온을 뺀 값입니다. "
    "잔차가 양수이면 실제 기온이 추세선보다 높고, "
    "음수이면 추세선보다 낮습니다."
)

# --------------------------------------------------
# 10. 선형회귀 알고리즘 설명
# --------------------------------------------------
st.subheader("🤖 사용한 알고리즘: 선형회귀")

st.markdown(
    """
    **선형회귀**는 과거 데이터의 경향을 가장 잘 나타내는 직선을 찾아
    새로운 값을 예측하는 방법입니다.

    1. **데이터 준비:** 선택한 월의 2007년부터 2025년까지의
       실제 평균기온 데이터를 모읍니다. 실제 시작 연도는 CSV 자료에 따라 달라집니다.
    2. **직선 찾기:** `numpy.polyfit()`으로 연도와 평균기온 사이의
       직선 관계를 계산합니다.
    3. **미래 예측:** 계산한 직선에 사용자가 선택한 연도를 넣어
       예측 평균기온을 구합니다.
    4. **잔차 확인:** 실제 기온과 추세선 기온의 차이를 계산해
       직선이 실제 데이터와 얼마나 다른지 확인합니다.

    **예측 공식**

    `예측 평균기온 = 기울기 × 예측 연도 + 절편`

    **결정계수 R²**는 추세선이 과거 데이터의 변화를 얼마나 설명하는지
    참고하는 지표입니다. 값이 높다고 해서 미래 예측이 반드시 정확한 것은 아닙니다.
    """
)

# --------------------------------------------------
# 11. 사용한 데이터 범위 표시
# --------------------------------------------------
st.subheader("📅 데이터 정보")

st.write(f"- 분석 월: {selected_month}월")
st.write(f"- 실제 데이터 범위: {int(years.min())}년 ~ 2025년")
st.write(f"- 분석에 사용한 연도별 데이터 수: {len(monthly_data)}개")
st.write(f"- 예측 대상 연도: {selected_year}년")
