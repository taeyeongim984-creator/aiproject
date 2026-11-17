
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
st.write("세 가지 회귀 알고리즘으로 기온을 예측하고 결과를 비교해 보세요.")

st.info("📌 실제 관측 데이터는 2025년까지 사용합니다.")

# --------------------------------------------------
# 2. CSV 파일 불러오기
# temperature.csv는 pages 폴더의 상위 폴더에 위치
# --------------------------------------------------
CSV_PATH = Path(__file__).resolve().parent.parent / "temperature.csv"

if not CSV_PATH.exists():
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "프로젝트 최상위 폴더에 CSV 파일을 넣어 주세요."
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
# 3. 열 이름 확인 및 데이터 정리
# --------------------------------------------------
date_col = "일시"
temp_col = "평균기온(℃)"

if date_col not in data.columns or temp_col not in data.columns:
    st.error(
        "CSV 파일의 열 이름을 확인해 주세요.\n\n"
        f"필요한 열: '{date_col}', '{temp_col}'\n\n"
        f"현재 열 이름: {list(data.columns)}"
    )
    st.stop()

date_text = data[date_col].astype(str).str.strip()

# 예: Oct-07
dates = pd.to_datetime(
    date_text,
    format="%b-%y",
    errors="coerce"
)

# 다른 날짜 형식에 대한 추가 처리
missing_dates = dates.isna()

if missing_dates.any():
    dates.loc[missing_dates] = pd.to_datetime(
        date_text.loc[missing_dates],
        errors="coerce"
    )

data["날짜"] = dates

data["평균기온"] = pd.to_numeric(
    data[temp_col].astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("℃", "", regex=False)
    .str.strip(),
    errors="coerce"
)

data = data.dropna(subset=["날짜", "평균기온"]).copy()

data["연도"] = data["날짜"].dt.year
data["월"] = data["날짜"].dt.month

# 실제 데이터는 2025년까지 제한
data = data[data["연도"] <= 2025].copy()

if data.empty:
    st.error("2025년까지의 유효한 기온 데이터가 없습니다.")
    st.stop()

# --------------------------------------------------
# 4. 사용자 입력
# --------------------------------------------------
st.subheader("🔎 예측 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:
    selected_month = st.selectbox(
        "예측할 월",
        list(range(1, 13)),
        format_func=lambda m: f"{m}월"
    )

with col2:
    selected_year = st.number_input(
        "예측할 연도",
        min_value=2026,
        max_value=2100,
        value=2026,
        step=1
    )

with col3:
    selected_algorithm = st.selectbox(
        "사용할 회귀 알고리즘",
        [
            "선형회귀",
            "2차 다항회귀",
            "3차 다항회귀"
        ]
    )

# --------------------------------------------------
# 5. 선택한 월의 연도별 평균기온 준비
# --------------------------------------------------
monthly_data = data[data["월"] == selected_month].copy()

monthly_data = (
    monthly_data.groupby("연도", as_index=False)["평균기온"]
    .mean()
    .sort_values("연도")
)

if len(monthly_data) < 4:
    st.error(
        "세 가지 알고리즘을 비교하려면 선택한 월에 "
        "최소 4개 연도의 유효한 데이터가 필요합니다."
    )
    st.stop()

years = monthly_data["연도"].to_numpy(dtype=float)
temperatures = monthly_data["평균기온"].to_numpy(dtype=float)

# 연도를 중심화해 다항회귀의 수치 계산을 안정적으로 수행
center_year = float(np.mean(years))
x = years - center_year

# --------------------------------------------------
# 6. 세 가지 회귀 알고리즘 학습
# NumPy의 polyfit 사용: 별도 머신러닝 라이브러리 불필요
# --------------------------------------------------
algorithms = {
    "선형회귀": 1,
    "2차 다항회귀": 2,
    "3차 다항회귀": 3
}

models = {}
predictions = {}
fitted_values = {}
r2_scores = {}

total_variation = np.sum(
    (temperatures - np.mean(temperatures)) ** 2
)

for name, degree in algorithms.items():
    coefficients = np.polyfit(x, temperatures, degree)
    models[name] = coefficients

    # 과거 관측 연도에 대한 추세선 값
    fitted = np.polyval(coefficients, x)
    fitted_values[name] = fitted

    # 선택한 예측 연도에 대한 예측값
    future_x = float(selected_year) - center_year
    predictions[name] = float(
        np.polyval(coefficients, future_x)
    )

    # 결정계수 R²
    residual_variation = np.sum((temperatures - fitted) ** 2)

    if total_variation > 0:
        r2_scores[name] = float(
            1 - residual_variation / total_variation
        )
    else:
        r2_scores[name] = 0.0

# --------------------------------------------------
# 7. 세 알고리즘의 예측값을 한눈에 비교
# --------------------------------------------------
st.subheader("📊 세 가지 알고리즘 예측 결과 비교")

comparison = pd.DataFrame({
    "알고리즘": list(algorithms.keys()),
    f"{selected_year}년 {selected_month}월 예측 기온(℃)": [
        predictions[name] for name in algorithms
    ],
    "결정계수 R²": [
        r2_scores[name] for name in algorithms
    ]
})

comparison[f"{selected_year}년 {selected_month}월 예측 기온(℃)"] = (
    comparison[
        f"{selected_year}년 {selected_month}월 예측 기온(℃)"
    ].round(2)
)

comparison["결정계수 R²"] = comparison["결정계수 R²"].round(3)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

# 세 가지 예측값을 각각 큰 숫자로 표시
metric_cols = st.columns(3)

for i, name in enumerate(algorithms.keys()):
    with metric_cols[i]:
        st.metric(
            label=name,
            value=f"{predictions[name]:.2f} ℃",
            delta=f"R² = {r2_scores[name]:.3f}"
        )

# --------------------------------------------------
# 8. 그래프
# 실제 기온 + 세 알고리즘의 추세선
# 선택한 알고리즘은 굵은 선으로 강조
# --------------------------------------------------
st.subheader(f"📈 {selected_month}월 평균기온 및 회귀선")

fig, ax = plt.subplots(figsize=(12, 6))

# 실제 관측 데이터
ax.scatter(
    years,
    temperatures,
    color="black",
    s=45,
    label="실제 평균기온 (2025년까지)",
    zorder=5
)

# 실제 관측값을 점선으로 연결
ax.plot(
    years,
    temperatures,
    linestyle=":",
    alpha=0.45,
    color="gray",
    label="실제 데이터 연결"
)

# 회귀선을 예측 연도까지 연장
line_years = np.linspace(
    float(years.min()),
    max(float(selected_year), float(years.max())),
    350
)

line_x = line_years - center_year

# 서로 구분되는 선 스타일 사용
line_styles = {
    "선형회귀": "-",
    "2차 다항회귀": "--",
    "3차 다항회귀": "-."
}

for name, degree in algorithms.items():
    line_y = np.polyval(models[name], line_x)

    is_selected = name == selected_algorithm

    ax.plot(
        line_years,
        line_y,
        linestyle=line_styles[name],
        linewidth=3.2 if is_selected else 1.7,
        alpha=1.0 if is_selected else 0.75,
        label=f"{name}" + (" (선택됨)" if is_selected else "")
    )

    # 선택한 예측값을 그래프에 표시
    if is_selected:
        ax.scatter(
            [selected_year],
            [predictions[name]],
            marker="*",
            s=240,
            color="red",
            edgecolors="black",
            zorder=10,
            label=f"선택 알고리즘 예측: {predictions[name]:.2f}℃"
        )

        ax.annotate(
            f"{predictions[name]:.2f}℃",
            (selected_year, predictions[name]),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=10
        )

ax.axvline(
    x=2025,
    linestyle=":",
    color="gray",
    alpha=0.8
)

ax.text(
    2025,
    0.98,
    "실제 데이터 마지막 연도",
    transform=ax.get_xaxis_transform(),
    ha="right",
    va="top",
    fontsize=9
)

ax.set_title(
    f"{selected_month}월 평균기온: 세 가지 회귀 알고리즘 비교"
)
ax.set_xlabel("연도")
ax.set_ylabel("평균기온 (℃)")
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# --------------------------------------------------
# 9. 선택한 알고리즘 설명
# --------------------------------------------------
st.subheader("🤖 선택한 알고리즘 설명")

algorithm_descriptions = {
    "선형회귀": """
**선형회귀**는 데이터를 가장 잘 나타내는 직선을 찾습니다.

- 기온이 장기적으로 상승하거나 하락하는 추세를 간단하게 나타냅니다.
- 기온 변화가 직선 형태라고 가정합니다.
""",
    "2차 다항회귀": """
**2차 다항회귀**는 곡선 형태의 추세를 학습합니다.

- 기온이 시간이 지나면서 상승과 하락의 방향을 바꾸는 경향을 표현할 수 있습니다.
- 직선보다 유연하지만, 실제 미래의 변화까지 보장하지는 않습니다.
""",
    "3차 다항회귀": """
**3차 다항회귀**는 더 복잡한 곡선 형태를 학습합니다.

- 기온 변화의 굴곡을 더 많이 표현할 수 있습니다.
- 과거 데이터에 지나치게 맞춰질 수 있어 미래 예측에서는 주의가 필요합니다.
"""
}

st.markdown(algorithm_descriptions[selected_algorithm])

st.write(
    f"**선택한 알고리즘:** {selected_algorithm}"
)
st.write(
    f"**{selected_year}년 {selected_month}월 예측 평균기온:** "
    f"{predictions[selected_algorithm]:.2f}℃"
)

# --------------------------------------------------
# 10. 실제 기온과 각 알고리즘의 추세선 비교
# --------------------------------------------------
st.subheader("🧾 실제 기온과 추세선 값 비교")

details = monthly_data[["연도", "평균기온"]].copy()
details = details.rename(
    columns={"평균기온": "실제 평균기온(℃)"}
)

for name in algorithms:
    details[f"{name} 추세선(℃)"] = fitted_values[name].round(2)
    details[f"{name} 잔차(℃)"] = (
        temperatures - fitted_values[name]
    ).round(2)

details["실제 평균기온(℃)"] = details["실제 평균기온(℃)"].round(2)

st.dataframe(
    details,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "잔차 = 실제 평균기온 - 알고리즘이 계산한 추세선 기온. "
    "잔차가 양수이면 실제 기온이 추세선보다 높고, "
    "음수이면 추세선보다 낮습니다."
)

# --------------------------------------------------
# 11. 알고리즘 비교 시 주의점
# --------------------------------------------------
with st.expander("💡 결과를 해석할 때 알아둘 점"):
    st.markdown(
        """
- **예측값**은 각 알고리즘이 계산한 선택 연도의 평균기온입니다.
- **R²(결정계수)**는 과거 데이터에서 추세선이 변화를 얼마나 설명하는지 보여 줍니다.
- R²가 높다고 해서 미래 예측이 반드시 더 정확한 것은 아닙니다.
- 2차·3차 다항회귀는 과거 데이터에 지나치게 맞춰질 수 있습니다.
- 실제 관측값은 2025년까지만 사용하며, 이후 그래프의 선은 예측 추세입니다.
- 이 프로그램은 월별 기온의 연도별 평균을 이용합니다. 계절별·연도별 기후 요인을
  별도로 학습하는 정교한 기후 예측 모델은 아닙니다.
        """
    )

st.caption(
    f"분석 월: {selected_month}월 | "
    f"실제 데이터: {int(years.min())}~2025년 | "
    f"예측 연도: {selected_year}년"
)
