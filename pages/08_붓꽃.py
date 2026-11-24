
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import ListedColormap
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="붓꽃 품종 예측",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측")
st.write(
    "꽃잎 길이와 너비를 입력하고 분류 알고리즘을 선택해 "
    "예측 결과와 작동 원리를 확인해 보세요."
)

# --------------------------------------------------
# 2. 그래프 글꼴 설정
#    packages.txt에서 한글 글꼴을 설치합니다.
# --------------------------------------------------
plt.rcParams["axes.unicode_minus"] = False

font_candidates = [
    "NanumGothic",
    "NanumBarunGothic",
    "Malgun Gothic",
    "AppleGothic"
]

font_found = False

for font_name in font_candidates:
    try:
        fm.findfont(font_name, fallback_to_default=False)
        plt.rcParams["font.family"] = font_name
        font_found = True
        break
    except ValueError:
        continue

# 그래프 제목과 축은 영어를 사용하므로
# 한글 글꼴이 없어도 그래프의 주요 문자는 표시됩니다.
if not font_found:
    plt.rcParams["font.family"] = "DejaVu Sans"

# --------------------------------------------------
# 3. CSV 파일 불러오기
#    pages 폴더의 상위 폴더에 Iris.csv가 있어야 합니다.
# --------------------------------------------------
csv_path = Path(__file__).resolve().parent.parent / "Iris.csv"

if not csv_path.exists():
    st.error(
        "Iris.csv 파일을 찾을 수 없습니다. "
        "저장소 최상위 폴더에 파일을 넣어 주세요."
    )
    st.stop()

try:
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp949")

    df.columns = df.columns.astype(str).str.strip()

except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없습니다: {e}")
    st.stop()

required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일에 필요한 열이 없습니다.\n\n"
        f"필요한 열: {required_columns}\n"
        f"현재 열: {list(df.columns)}"
    )
    st.stop()

df = df[required_columns].copy()

df["꽃잎 길이"] = pd.to_numeric(
    df["꽃잎 길이"], errors="coerce"
)
df["꽃잎 너비"] = pd.to_numeric(
    df["꽃잎 너비"], errors="coerce"
)
df["품종"] = df["품종"].astype("string").str.strip()

df = df.dropna()
df = df[df["품종"] != ""]

if len(df) < 10 or df["품종"].nunique() < 2:
    st.error("분류에 사용할 데이터가 충분하지 않습니다.")
    st.stop()

# --------------------------------------------------
# 4. 데이터 준비
# --------------------------------------------------
feature_columns = ["꽃잎 길이", "꽃잎 너비"]
X = df[feature_columns]
y = df["품종"].astype(str)

species_list = sorted(y.unique())
species_count = len(species_list)

base_colors = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#B279A2",
    "#E45756",
    "#72B7B2"
]

species_colors = {
    species: base_colors[i % len(base_colors)]
    for i, species in enumerate(species_list)
}

if y.value_counts().min() < 2:
    st.error("각 품종에는 최소 2개의 데이터가 필요합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# --------------------------------------------------
# 5. 세 가지 알고리즘 생성
# --------------------------------------------------
def make_models():
    return {
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "결정 트리": DecisionTreeClassifier(
            max_depth=4,
            random_state=42
        ),
        "랜덤 포레스트": RandomForestClassifier(
            n_estimators=100,
            max_depth=4,
            random_state=42
        )
    }

# 테스트 데이터로 정확도 계산
evaluation_models = make_models()
accuracy_results = {}

for name, model in evaluation_models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    accuracy_results[name] = accuracy_score(
        y_test, predictions
    )

# 전체 데이터로 최종 모델 학습
models = make_models()

for model in models.values():
    model.fit(X, y)

# --------------------------------------------------
# 6. 알고리즘 선택
# --------------------------------------------------
st.subheader("🧠 알고리즘 선택")

selected_algorithm = st.selectbox(
    "확인할 알고리즘을 선택하세요.",
    ["KNN", "결정 트리", "랜덤 포레스트"]
)

# --------------------------------------------------
# 7. 꽃잎 길이와 너비 입력
# --------------------------------------------------
st.subheader("📝 꽃잎 정보 입력")

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())
width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

col1, col2 = st.columns(2)

with col1:
    st.caption(
        f"입력 가능 범위: {length_min:.1f} ~ {length_max:.1f} cm"
    )
    petal_length = st.number_input(
        "꽃잎 길이 (cm)",
        min_value=length_min,
        max_value=length_max,
        value=float(df["꽃잎 길이"].median()),
        step=0.1,
        format="%.1f"
    )

with col2:
    st.caption(
        f"입력 가능 범위: {width_min:.1f} ~ {width_max:.1f} cm"
    )
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(df["꽃잎 너비"].median()),
        step=0.1,
        format="%.1f"
    )

input_data = pd.DataFrame({
    "꽃잎 길이": [petal_length],
    "꽃잎 너비": [petal_width]
})

# --------------------------------------------------
# 8. 선택한 알고리즘의 예측 결과
# --------------------------------------------------
selected_model = models[selected_algorithm]
prediction = selected_model.predict(input_data)[0]
probabilities = selected_model.predict_proba(input_data)[0]
confidence = float(np.max(probabilities))

st.subheader("🔍 예측 결과")

result_col1, result_col2 = st.columns(2)

with result_col1:
    st.metric("예측 품종", prediction)

with result_col2:
    st.metric("예측 확률", f"{confidence * 100:.1f}%")

st.caption(
    "예측 확률은 모델이 계산한 값이며, "
    "실제 정답일 가능성을 보장하지는 않습니다."
)

st.write("**품종별 예측 확률**")

probability_df = pd.DataFrame({
    "품종": selected_model.classes_,
    "예측 확률 (%)": np.round(probabilities * 100, 1)
})

st.dataframe(
    probability_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# 9. 선택한 알고리즘의 그래프
#    그래프의 제목과 축은 영어로 표시해 글꼴 문제 방지
# --------------------------------------------------
st.subheader("📊 품종 분류 그래프")

st.write(
    "배경색은 알고리즘이 예측하는 품종 영역입니다. "
    "점은 실제 데이터이고 노란색 별은 입력한 값입니다."
)

x_padding = max((length_max - length_min) * 0.08, 0.1)
y_padding = max((width_max - width_min) * 0.08, 0.1)

x_values = np.linspace(
    length_min - x_padding,
    length_max + x_padding,
    180
)
y_values = np.linspace(
    width_min - y_padding,
    width_max + y_padding,
    180
)

xx, yy = np.meshgrid(x_values, y_values)

grid_data = pd.DataFrame({
    "꽃잎 길이": xx.ravel(),
    "꽃잎 너비": yy.ravel()
})

species_to_number = {
    species: i for i, species in enumerate(species_list)
}

grid_predictions = selected_model.predict(grid_data)

grid_numbers = np.array([
    species_to_number[s]
    for s in grid_predictions
]).reshape(xx.shape)

class_cmap = ListedColormap([
    species_colors[species]
    for species in species_list
])

fig, ax = plt.subplots(figsize=(9, 6))

ax.contourf(
    xx,
    yy,
    grid_numbers,
    levels=np.arange(species_count + 1) - 0.5,
    cmap=class_cmap,
    alpha=0.22
)

for species in species_list:
    species_data = df[df["품종"].astype(str) == species]

    ax.scatter(
        species_data["꽃잎 길이"],
        species_data["꽃잎 너비"],
        color=species_colors[species],
        edgecolors="white",
        linewidths=0.5,
        s=35,
        alpha=0.85,
        label=species
    )

# 입력한 데이터는 노란색 별로 표시
ax.scatter(
    petal_length,
    petal_width,
    marker="*",
    s=350,
    color="#FFD700",
    edgecolors="black",
    linewidths=1.2,
    zorder=10,
    label="Your input"
)

# 그래프 제목은 영어로 표시
english_names = {
    "KNN": "K-Nearest Neighbors",
    "결정 트리": "Decision Tree",
    "랜덤 포레스트": "Random Forest"
}

ax.set_title(
    f"{english_names[selected_algorithm]} - Prediction: {prediction}",
    fontsize=13
)
ax.set_xlabel("Petal length (cm)")
ax.set_ylabel("Petal width (cm)")
ax.grid(True, linestyle="--", alpha=0.25)
ax.legend(loc="best", fontsize=9)

fig.tight_layout()
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# --------------------------------------------------
# 10. 선택한 알고리즘의 작동 원리
# --------------------------------------------------
st.subheader("⚙️ 작동 원리")

if selected_algorithm == "KNN":
    st.markdown(
        """
        **KNN: 가까운 이웃을 이용한 분류**

        1. 입력한 꽃잎 길이와 너비를 학습 데이터와 비교합니다.
        2. 가까운 이웃 5개를 찾습니다.
        3. 이웃에서 가장 많이 나타난 품종을 예측합니다.

        **그래프 해석:** 입력한 별 주변에 어떤 품종의 점이
        모여 있는지 확인해 보세요.
        """
    )

elif selected_algorithm == "결정 트리":
    st.markdown(
        """
        **결정 트리: 조건을 따라 분류하기**

        1. 꽃잎 길이와 너비를 기준으로 나누는 조건을 학습합니다.
        2. 조건을 순서대로 적용해 데이터 영역을 나눕니다.
        3. 해당 영역의 학습 결과를 바탕으로 품종을 예측합니다.

        **그래프 해석:** 배경색이 바뀌는 경계를 살펴보세요.
        """
    )

else:
    st.markdown(
        """
        **랜덤 포레스트: 여러 결정 트리의 결과 결합**

        1. 서로 다른 표본과 특징을 활용해 여러 트리를 만듭니다.
        2. 각 트리가 입력한 꽃잎의 품종을 예측합니다.
        3. 여러 트리의 예측을 모아 최종 품종을 결정합니다.

        **그래프 해석:** 여러 트리의 결과가 결합된 분류 영역을
        확인해 보세요.
        """
    )

# --------------------------------------------------
# 11. 세 알고리즘 정확도 비교
# --------------------------------------------------
st.subheader("📈 세 알고리즘 정확도 비교")

accuracy_df = pd.DataFrame({
    "Algorithm": list(accuracy_results.keys()),
    "Accuracy (%)": [
        round(score * 100, 1)
        for score in accuracy_results.values()
    ]
})

# 그래프의 축과 범례는 영어로 표시
fig2, ax2 = plt.subplots(figsize=(8, 4))

bars = ax2.bar(
    accuracy_df["Algorithm"],
    accuracy_df["Accuracy (%)"],
    color=["#4C78A8", "#F58518", "#54A24B"]
)

ax2.set_title("Algorithm Accuracy Comparison")
ax2.set_xlabel("Algorithm")
ax2.set_ylabel("Test accuracy (%)")
ax2.set_ylim(0, 100)
ax2.grid(axis="y", linestyle="--", alpha=0.3)

for bar in bars:
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        height + 1,
        f"{height:.1f}%",
        ha="center",
        va="bottom"
    )

fig2.tight_layout()
st.pyplot(fig2, use_container_width=True)
plt.close(fig2)

st.caption(
    "정확도는 데이터를 학습용 80%, 테스트용 20%로 나누어 계산합니다. "
    "데이터 분할과 모델 설정에 따라 결과가 달라질 수 있습니다."
)

# --------------------------------------------------
# 12. 원본 데이터
# --------------------------------------------------
with st.expander("📄 붓꽃 데이터 확인하기"):
    st.write(f"전체 데이터 수: {len(df)}개")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.write("품종별 데이터 수")
    st.dataframe(
        df["품종"].value_counts().rename("데이터 수"),
        use_container_width=True
    )
