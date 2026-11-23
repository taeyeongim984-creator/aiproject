
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 AI 붓꽃 품종 예측")
st.write("꽃잎 길이와 꽃잎 너비를 입력하여 붓꽃 품종을 예측해 보세요.")

# ==========================================
# 2. CSV 파일 불러오기
# pages 폴더의 상위 폴더에서 Iris.csv 찾기
# ==========================================
csv_path = Path(__file__).resolve().parent.parent / "Iris.csv"

if not csv_path.exists():
    st.error(f"Iris.csv 파일을 찾을 수 없습니다: {csv_path}")
    st.stop()

try:
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp949")
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

# 열 이름의 앞뒤 공백 제거
df.columns = df.columns.astype(str).str.strip()

# 필요한 열 확인
required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 열 이름을 확인해 주세요.")
    st.write("현재 CSV 열 이름:", df.columns.tolist())
    st.stop()

# 분석에 필요한 데이터만 선택
df = df[required_columns].copy()

df["꽃잎 길이"] = pd.to_numeric(
    df["꽃잎 길이"], errors="coerce"
)
df["꽃잎 너비"] = pd.to_numeric(
    df["꽃잎 너비"], errors="coerce"
)

df = df.dropna()

if len(df) < 5 or df["품종"].nunique() < 2:
    st.error("품종 예측에 사용할 데이터가 부족합니다.")
    st.stop()

# ==========================================
# 3. 입력 가능한 범위 계산
# ==========================================
length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())
width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

st.info(
    f"📏 꽃잎 길이: {length_min:.1f} ~ {length_max:.1f}\n\n"
    f"📐 꽃잎 너비: {width_min:.1f} ~ {width_max:.1f}"
)

# ==========================================
# 4. KNN 분류 모델 학습 및 평가
# ==========================================
X = df[["꽃잎 길이", "꽃잎 너비"]]
y = df["품종"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)

test_predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, test_predictions)

# 예측에는 전체 데이터를 사용
model.fit(X, y)

# ==========================================
# 5. 사용자 입력
# ==========================================
st.subheader("🧪 꽃잎 크기 입력")

col1, col2 = st.columns(2)

with col1:
    petal_length = st.number_input(
        "꽃잎 길이",
        min_value=length_min,
        max_value=length_max,
        value=min(max(5.0, length_min), length_max),
        step=0.1,
        format="%.1f"
    )

with col2:
    petal_width = st.number_input(
        "꽃잎 너비",
        min_value=width_min,
        max_value=width_max,
        value=min(max(1.5, width_min), width_max),
        step=0.1,
        format="%.1f"
    )

st.caption(
    "입력값을 변경하면 그래프의 노란색 별 위치도 자동으로 변경됩니다."
)

predict_button = st.button(
    "🔍 품종 예측하기",
    type="primary",
    use_container_width=True
)

# ==========================================
# 6. 산점도 그리기
# 그래프 글자는 영어로 표시해 한글 깨짐 방지
# ==========================================
st.subheader("📊 꽃잎 길이와 너비의 관계")

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

species_names = sorted(df["품종"].unique())

# 품종별 색상
palette = [
    "#4285F4", "#34A853", "#EA4335",
    "#9467BD", "#FF7F0E", "#17BECF"
]

for i, species in enumerate(species_names):
    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        label=str(species),
        color=palette[i % len(palette)],
        s=60,
        alpha=0.8,
        edgecolors="white",
        linewidths=0.5
    )

# 사용자가 입력한 위치
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=500,
    color="#FFD700",
    edgecolors="black",
    linewidths=1.2,
    label="Your Input",
    zorder=10
)

ax.set_title(
    "Iris Petal Length vs Petal Width",
    fontsize=15,
    fontweight="bold",
    pad=15
)

ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)

ax.set_xlim(length_min - 0.3, length_max + 0.3)
ax.set_ylim(width_min - 0.15, width_max + 0.15)

ax.set_facecolor("#FAFAFA")
ax.grid(True, linestyle="--", linewidth=0.6, alpha=0.3)
ax.set_axisbelow(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(title="Species", frameon=True, loc="best")
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)

# ==========================================
# 7. 예측 결과
# ==========================================
if predict_button:
    input_data = pd.DataFrame(
        [[petal_length, petal_width]],
        columns=["꽃잎 길이", "꽃잎 너비"]
    )

    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    st.divider()
    st.subheader("🎯 예측 결과")

    st.success(f"예측된 붓꽃 품종: {prediction}")

    result_col1, result_col2 = st.columns(2)

    result_col1.metric("꽃잎 길이", f"{petal_length:.1f}")
    result_col2.metric("꽃잎 너비", f"{petal_width:.1f}")

    st.write("### 품종별 예측 비율")

    probability_df = pd.DataFrame({
        "품종": model.classes_,
        "예측 비율 (%)": probabilities * 100
    }).sort_values("예측 비율 (%)", ascending=False)

    st.dataframe(
        probability_df.style.format({
            "예측 비율 (%)": "{:.1f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "KNN의 예측 비율은 가까운 이웃 데이터의 품종 비율이며, "
        "실제 품종일 확률을 보장하지 않습니다."
    )

    st.metric("테스트 데이터 정확도", f"{accuracy:.1%}")

# ==========================================
# 8. 데이터 미리보기
# ==========================================
with st.expander("📚 학습 데이터 확인하기"):
    st.dataframe(df, use_container_width=True)

    st.write("품종별 데이터 개수")
    st.dataframe(
        df["품종"].value_counts().rename("데이터 개수"),
        use_container_width=True
    )

st.caption("붓꽃 데이터 기반 교육용 AI 분류 프로그램")
