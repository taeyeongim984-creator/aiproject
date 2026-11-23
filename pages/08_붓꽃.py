
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ------------------------------------
# 1. 페이지 설정
# ------------------------------------
st.set_page_config(
    page_title="🌸 붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측")
st.write(
    "꽃잎 길이와 꽃잎 너비를 입력하면 "
    "KNN 알고리즘이 붓꽃의 품종을 예측합니다."
)

st.info(
    "📏 입력 범위: 꽃잎 길이 1.0~6.9, "
    "꽃잎 너비 0.1~2.5\n\n"
    "위 범위는 업로드한 Iris.csv 데이터의 최솟값과 최댓값입니다."
)

# ------------------------------------
# 2. CSV 파일 불러오기
# ------------------------------------
@st.cache_data
def load_data():
    data = pd.read_csv("Iris.csv", encoding="cp949")

    # 열 이름의 앞뒤 공백 제거
    data.columns = data.columns.str.strip()

    # 필요한 열만 선택
    data = data[["꽃잎 길이", "꽃잎 너비", "품종"]]

    # 결측치 제거
    data = data.dropna()

    return data


try:
    df = load_data()
except Exception as e:
    st.error(
        "Iris.csv 파일을 불러오지 못했습니다. "
        "app.py와 같은 폴더에 파일이 있는지 확인해 주세요."
    )
    st.stop()

# ------------------------------------
# 3. 입력 범위 계산
# ------------------------------------
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())

width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

# ------------------------------------
# 4. KNN 분류 모델 학습
# ------------------------------------
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

# 데이터가 충분할 때 학습 및 평가용 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# KNN 모델: 가장 가까운 5개 데이터로 품종 결정
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)

# 테스트 데이터 정확도
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# 실제 예측용 모델은 전체 데이터로 다시 학습
model.fit(X, y)

# ------------------------------------
# 5. 사용자 입력
# ------------------------------------
st.subheader("🧪 꽃잎 정보 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "🌱 꽃잎 길이",
        min_value=length_min,
        max_value=length_max,
        value=5.0,
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "🌿 꽃잎 너비",
        min_value=width_min,
        max_value=width_max,
        value=1.5,
        step=0.1,
        format="%.1f"
    )

st.caption(
    f"꽃잎 길이: {length_min:.1f}~{length_max:.1f} | "
    f"꽃잎 너비: {width_min:.1f}~{width_max:.1f}"
)

predict_button = st.button(
    "🔍 품종 예측하기",
    type="primary",
    use_container_width=True
)

# ------------------------------------
# 6. 산점도 그리기
# ------------------------------------
st.subheader("📊 꽃잎 길이와 너비의 관계")
st.write(
    "색깔별 점은 CSV 파일에 있는 붓꽃 데이터이며, "
    "노란색 별은 사용자가 입력한 위치입니다."
)

fig, ax = plt.subplots(figsize=(10, 6))

species_names = sorted(df["품종"].unique())

# 품종별 데이터 표시
for species in species_names:
    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        label=species,
        alpha=0.75,
        s=55
    )

# 사용자가 입력한 지점을 노란색 별로 표시
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=450,
    c="yellow",
    edgecolors="black",
    linewidths=1.2,
    label="내 입력값",
    zorder=10
)

ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)
ax.set_title("Iris Petal Length vs Petal Width", fontsize=15)

ax.grid(True, linestyle="--", alpha=0.3)
ax.legend()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ------------------------------------
# 7. 품종 예측 결과
# ------------------------------------
if predict_button:
    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    st.divider()
    st.subheader("🎯 AI 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        st.metric(
            "입력한 꽃잎 길이",
            f"{petal_length:.1f}"
        )

    with result_col2:
        st.metric(
            "입력한 꽃잎 너비",
            f"{petal_width:.1f}"
        )

    st.write("### 품종별 모델 예측 확률")

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 확률(%)": probabilities * 100
    }).sort_values("예측 확률(%)", ascending=False)

    st.dataframe(
        probability_df.style.format(
            {"예측 확률(%)": "{:.1f}%"}
        ),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "예측 확률은 KNN의 이웃 데이터 중 각 품종이 차지하는 "
        "비율입니다. 실제 품종일 확률을 보장하지는 않습니다."
    )

    st.info(
        f"참고용 테스트 정확도: {accuracy * 100:.1f}% "
        "(전체 데이터 중 20%를 테스트에 사용)"
    )

# ------------------------------------
# 8. 데이터 미리보기
# ------------------------------------
with st.expander("📚 학습에 사용한 데이터 확인"):
    st.dataframe(df, use_container_width=True)

    st.write("품종별 데이터 개수")
    st.dataframe(
        df["품종"].value_counts().rename("개수"),
        use_container_width=True
    )

st.caption(
    "본 앱은 교육용 붓꽃 데이터 분석 및 품종 분류 프로그램입니다."
)
