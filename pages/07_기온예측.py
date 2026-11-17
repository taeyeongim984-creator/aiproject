
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.linear_model import LinearRegression

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
    "과거의 월별 평균기온 데이터를 이용해 "
    "선형회귀 알고리즘으로 미래 기온을 예측합니다."
)

# --------------------------------------------------
# 2. CSV 파일 불러오기
# 파이썬 파일은 pages 폴더에 있고,
# CSV 파일은 그 상위 폴더에 있음
# --------------------------------------------------
CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "temperature.csv"
)


@st.cache_data
def load_data(file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            "temperature.csv 파일을 프로젝트 최상위 폴더에 넣어주세요."
        )

    # CSV 파일 인코딩 처리
    try:
        data = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="utf-8-sig")

    # 필요한 열이 있는지 확인
    required_columns = ["일시", "평균기온(℃)"]

    for column in required_columns:
        if column not in data.columns:
            raise ValueError(
                f"CSV 파일에 '{column}' 열이 없습니다."
            )

    # 날짜 변환: 예) Oct-07
    data["일시"] = pd.to_datetime(
        data["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 평균기온을 숫자로 변환
    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    # 결측 데이터 제거
    data = data.dropna(
        subset=["일시", "평균기온(℃)"]
    ).copy()

    # 연도와 월 추출
    data["연도"] = data["일시"].dt.year
    data["월"] = data["일시"].dt.month

    return data.sort_values("일시")


try:
    df = load_data(CSV_PATH)

except Exception as error:
    st.error(f"데이터를 불러오지 못했습니다: {error}")
    st.stop()


if df.empty:
    st.error("분석할 수 있는 기온 데이터가 없습니다.")
    st.stop()


# --------------------------------------------------
# 3. 사용자 입력
# --------------------------------------------------
st.subheader("📌 예측 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "예측할 월을 선택하세요",
        options=list(range(1, 13)),
        format_func=lambda month: f"{month}월"
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


# --------------------------------------------------
# 4. 선택한 월의 모든 연도 데이터 추출
# --------------------------------------------------
month_data = df[
    df["월"] == selected_month
].copy()

month_data = month_data.sort_values("연도")

if len(month_data) < 2:
    st.warning(
        f"{selected_month}월의 데이터가 부족합니다. "
        "선형회귀를 계산하려면 서로 다른 연도의 데이터가 필요합니다."
    )
    st.stop()


# --------------------------------------------------
# 5. 선형회귀 모델 학습
# X: 연도
# Y: 평균기온
# --------------------------------------------------
X = month_data[["연도"]].to_numpy(dtype=float)

Y = month_data["평균기온(℃)"].to_numpy(dtype=float)

# 선형회귀 모델 생성
model = LinearRegression()

# 과거 데이터로 학습
model.fit(X, Y)

# 과거 연도별 회귀 예측값
fitted_values = model.predict(X)

# 사용자가 입력한 연도의 기온 예측
predicted_temperature = model.predict(
    np.array([[selected_year]], dtype=float)
)[0]

# 회귀선 기울기와 절편
slope = model.coef_[0]
intercept = model.intercept_

# 결정계수
r_squared = model.score(X, Y)


# --------------------------------------------------
# 6. 예측 결과
# --------------------------------------------------
st.subheader("🔮 기온 예측 결과")

result1, result2, result3 = st.columns(3)

with result1:
    st.metric(
        label=f"{selected_year}년 {selected_month}월 예측 평균기온",
        value=f"{predicted_temperature:.1f} °C"
    )

with result2:
    st.metric(
        label="회귀선 기울기",
        value=f"{slope:.3f} °C/년"
    )

with result3:
    st.metric(
        label="결정계수 (R²)",
        value=f"{r_squared:.3f}"
    )

st.caption(
    "예측값은 과거 자료에 나타난 선형적인 경향을 바탕으로 계산한 값이며, "
    "실제 기온과 다를 수 있습니다."
)


# --------------------------------------------------
# 7. 그래프 시각화
# --------------------------------------------------
st.subheader(
    f"📈 {selected_month}월 평균기온 및 선형회귀 그래프"
)

# 한글 글꼴 설정
plt.rcParams["font.family"] = [
    "Malgun Gothic",
    "AppleGothic",
    "DejaVu Sans"
]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 6))

years = month_data["연도"].to_numpy(dtype=float)
temperatures = month_data["평균기온(℃)"].to_numpy(dtype=float)

# 1) 실제 관측 기온
ax.scatter(
    years,
    temperatures,
    color="royalblue",
    s=55,
    label="실제 평균기온",
    zorder=4
)

# 2) 과거 데이터 범위의 회귀선
historical_x = np.linspace(
    years.min(),
    years.max(),
    200
).reshape(-1, 1)

historical_y = model.predict(historical_x)

ax.plot(
    historical_x.ravel(),
    historical_y,
    color="darkorange",
    linewidth=2.5,
    label="선형회귀 추세선",
    zorder=2
)

# 3) 실제 기온과 회귀 예측값 사이의 잔차
for year, actual, fitted in zip(
    years, temperatures, fitted_values
):
    ax.plot(
        [year, year],
        [actual, fitted],
        color="gray",
        alpha=0.4,
        linewidth=0.9,
        zorder=1
    )

# 4) 선택한 연도까지 회귀선 연장
if selected_year != years.max():
    extension_x = np.linspace(
        years.max(),
        selected_year,
        100
    ).reshape(-1, 1)

    extension_y = model.predict(extension_x)

    if selected_year > years.max():
        extension_label = "미래 예측 구간"
    else:
        extension_label = "과거 방향 추정 구간"

    ax.plot(
        extension_x.ravel(),
        extension_y,
        color="darkorange",
        linestyle="--",
        linewidth=2.5,
        label=extension_label,
        zorder=3
    )

# 5) 예측 기온 표시
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

ax.annotate(
    f"{predicted_temperature:.1f}°C",
    xy=(selected_year, predicted_temperature),
    xytext=(8, 12),
    textcoords="offset points",
    color="crimson",
    fontsize=11,
    fontweight="bold"
)

# 그래프 제목과 축
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
# 8. 전체 기온 데이터 표
# --------------------------------------------------
with st.expander("📋 선택한 월의 전체 기온 데이터 확인"):
    display_data = month_data[
        ["일시", "연도", "평균기온(℃)"]
    ].copy()

    display_data["일시"] = (
        display_data["일시"].dt.strftime("%Y년 %m월")
    )

    display_data = display_data.rename(
        columns={
            "일시": "관측 월",
            "연도": "연도",
            "평균기온(℃)": "평균기온(℃)"
        }
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 9. 선형회귀 알고리즘 설명
# --------------------------------------------------
st.divider()

st.subheader("🧠 선형회귀 알고리즘 쉽게 이해하기")

st.markdown("""
### ① 파란색 점: 실제 평균기온
CSV 파일에 기록된 각 연도의 실제 평균기온입니다.
점 하나가 해당 연도의 선택한 월 평균기온을 나타냅니다.

### ② 주황색 실선: 선형회귀 추세선
선형회귀 모델이 과거의 연도와 평균기온 데이터를 학습해 계산한 직선입니다.
실제 데이터와 직선 사이의 세로 방향 차이를 전체적으로 작게 만드는 직선을 찾습니다.

- 직선이 오른쪽 위로 올라가면 장기적인 상승 경향을 뜻합니다.
- 직선이 오른쪽 아래로 내려가면 장기적인 하락 경향을 뜻합니다.

### ③ 회색 세로선: 잔차(예측 오차)
각 실제 기온과 회귀선이 계산한 기온 사이의 차이를 보여줍니다.
세로선이 짧을수록 실제 관측값이 회귀선에 가깝습니다.

### ④ 빨간색 별표: 예측 기온
사용자가 선택한 연도를 선형회귀 모델에 입력해 계산한 예상 평균기온입니다.

미래 연도를 선택하면 주황색 점선이 예측 연도까지 이어집니다.
이처럼 기존 데이터의 범위 바깥으로 직선을 연장해 값을 추정하는 것을
**외삽**이라고 합니다.

### 📐 선형회귀는 어떻게 계산할까요?

선형회귀는 다음과 같은 직선의 식을 사용합니다.

**예측 평균기온 = 기울기 × 연도 + 절편**

- **기울기:** 연도가 1년 증가할 때 회귀선의 기온이 얼마나 변하는지 나타냅니다.
- **절편:** 회귀 직선의 위치를 결정하는 값입니다.
- **학습:** `model.fit()`이 과거 연도와 기온의 관계를 계산합니다.
- **예측:** `model.predict()`가 학습한 관계를 이용해 선택한 연도의 기온을 추정합니다.
- **결정계수 R²:** 회귀선이 과거 기온 데이터의 변동을 얼마나 설명하는지 보여줍니다.
  1에 가까울수록 데이터에 대한 설명력이 높으며, 음수가 나올 수도 있습니다.

💡 **주의:** 기온은 계절, 강수, 기후 변화 등 다양한 요인의 영향을 받습니다.
이 프로그램은 과거의 선형적인 경향만 이용하므로 실제 기상예보와는 다릅니다.
""")

st.info(
    "💡 그래프 읽기: 파란색 점은 실제 기온, 주황색 실선은 학습한 추세, "
    "회색 세로선은 잔차, 빨간색 별표는 예측 기온입니다."
)
