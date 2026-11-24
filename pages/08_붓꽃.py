
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from matplotlib.colors import ListedColormap

# --------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="붓꽃 분류 알고리즘 비교",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 및 알고리즘 비교")
st.write(
    "꽃잎 길이와 너비를 입력하고, "
    "3가지 분류 알고리즘이 어떤 품종으로 예측하는지 비교해 보세요."
)

# --------------------------------------------------
# 2. CSV 파일 불러오기
#    pages 폴더의 상위 폴더에 Iris.csv가 있어야 함
# --------------------------------------------------
csv_path = Path(__file__).resolve().parent.parent / "Iris.csv"

if not csv_path.exists():
    st.error(
        "Iris.csv 파일을 찾을 수 없습니다. "
        "저장소의 최상위 폴더에 Iris.csv를 넣어 주세요."
    )
    st.stop()

try:
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding="cp949")

    # 열 이름의 앞뒤 공백 제거
    df.columns = df.columns.astype(str).str.strip()

except Exception as e:
    st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {e}")
    st.stop()

required_columns = ["꽃잎 길이", "꽃잎 너비", "품종"]

if not all(col in df.columns for col in required_columns):
    st.error(
        "CSV 파일에 필요한 열이 없습니다.\n\n"
        "필요한 열: 꽃잎 길이, 꽃잎 너비, 품종\n\n"
        f"현재 열 이름: {list(df.columns)}"
    )
    st.stop()

# 필요한 열만 사용하고 숫자 변환
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
    st.error("분류 학습에 사용할 데이터가 충분하지 않습니다.")
    st.stop()

# --------------------------------------------------
# 3. 학습 데이터 준비
# --------------------------------------------------
feature_columns = ["꽃잎 길이", "꽃잎 너비"]

X = df[feature_columns]
y = df["품종"].astype(str)

species_list = sorted(y.unique())
species_count = len(species_list)

# 그래프에 사용할 품종별 색상
base_colors = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#B279A2",
    "#E45756",
    "#72B7B2",
]

species_colors = {
    species: base_colors[i % len(base_colors)]
    for i, species in enumerate(species_list)
}

# --------------------------------------------------
# 4. 3가지 알고리즘 만들기
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
        ),
    }


# --------------------------------------------------
# 5. 정확도 평가용 학습과 테스트
# --------------------------------------------------
class_counts = y.value_counts()

# 각 품종에 데이터가 2개 이상 있어야 계층 분할 가능
if class_counts.min() < 2:
    st.error("각 품종에 최소 2개 이상의 데이터가 필요합니다.")
    st.stop()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

evaluation_models = make_models()
accuracy_results = {}

for name, model in evaluation_models.items():
    model.fit(X_train, y_train)
    test_predictions = model.predict(X_test)

    accuracy_results[name] = accuracy_score(
        y_test, test_predictions
    )

# 실제 예측과 결정 경계 그래프는 전체 데이터로 학습한 모델 사용
models = make_models()

for model in models.values():
    model.fit(X, y)

# --------------------------------------------------
# 6. 사용자 입력
# --------------------------------------------------
st.subheader("📝 꽃잎 정보 입력")

length_min = float(df["꽃잎 길이"].min())
length_max = float(df["꽃잎 길이"].max())
width_min = float(df["꽃잎 너비"].min())
width_max = float(df["꽃잎 너비"].max())

col1, col2 = st.columns(2)

with col1:
    st.caption(
        f"꽃잎 길이의 데이터 범위: "
        f"{length_min:.1f} ~ {length_max:.1f} cm"
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
        f"꽃잎 너비의 데이터 범위: "
        f"{width_min:.1f} ~ {width_max:.1f} cm"
    )
    petal_width = st.number_input(
        "꽃잎 너비 (cm)",
        min_value=width_min,
        max_value=width_max,
        value=float(df["꽃잎 너비"].median()),
        step=0.1,
        format="%.1f"
    )

input_data = pd.DataFrame(
    {
        "꽃잎 길이": [petal_length],
        "꽃잎 너비": [petal_width],
    }
)

# --------------------------------------------------
# 7. 알고리즘별 예측 결과
# --------------------------------------------------
st.subheader("🔎 알고리즘별 예측 결과")

result_rows = []

for name, model in models.items():
    predicted_species = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(np.max(probabilities))

    result_rows.append(
        {
            "알고리즘": name,
            "예측 품종": predicted_species,
            "예측 확률": f"{confidence * 100:.1f}%",
            "테스트 정확도": f"{accuracy_results[name] * 100:.1f}%",
        }
    )

result_df = pd.DataFrame(result_rows)

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# 8. 알고리즘별 예측을 카드로 표시
# --------------------------------------------------
st.subheader("🌼 세 가지 예측 한눈에 보기")

result_columns = st.columns(3)

for i, (name, model) in enumerate(models.items()):
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    confidence = float(np.max(probabilities))

    with result_columns[i]:
        st.markdown(f"### {name}")
        st.markdown(f"**예측 품종: {prediction}**")
        st.metric(
            "예측 확률",
            f"{confidence * 100:.1f}%"
        )
        st.metric(
            "테스트 정확도",
            f"{accuracy_results[name] * 100:.1f}%"
        )

# --------------------------------------------------
# 9. 세 알고리즘의 작동 원리 시각화
# --------------------------------------------------
st.subheader("📊 알고리즘은 어떻게 품종을 나눌까요?")
st.write(
    "배경색은 각 알고리즘이 해당 위치에서 예측하는 품종을 나타냅니다. "
    "점은 실제 데이터이고, 노란색 별은 입력한 꽃잎 정보입니다. "
    "배경색의 경계가 알고리즘마다 다르면 품종을 나누는 방식도 "
    "다르다는 뜻입니다."
)

# 그래프의 한글 깨짐을 피하기 위해 축과 범례는 영어로 표시
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# 모든 그래프에서 같은 축 범위 사용
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

grid_data = pd.DataFrame(
    {
        "꽃잎 길이": xx.ravel(),
        "꽃잎 너비": yy.ravel(),
    }
)

# 배경색에 사용할 품종 번호
species_to_number = {
    species: i for i, species in enumerate(species_list)
}

class_cmap = ListedColormap(
    [
        species_colors[species]
        for species in species_list
    ]
)

fig, axes = plt.subplots(
    1, 3,
    figsize=(18, 5),
    sharex=True,
    sharey=True
)

for ax, (name, model) in zip(axes, models.items()):
    # 각 위치에서 알고리즘이 예측한 품종
    grid_predictions = model.predict(grid_data)

    grid_numbers = np.array(
        [species_to_number[s] for s in grid_predictions]
    ).reshape(xx.shape)

    # 결정 영역: 알고리즘이 품종을 구분하는 영역
    ax.contourf(
        xx,
        yy,
        grid_numbers,
        levels=np.arange(species_count + 1) - 0.5,
        cmap=class_cmap,
        alpha=0.22
    )

    # 실제 데이터 점 표시
    for species in species_list:
        species_data = df[df["품종"].astype(str) == species]

        ax.scatter(
            species_data["꽃잎 길이"],
            species_data["꽃잎 너비"],
            color=species_colors[species],
            edgecolors="white",
            linewidths=0.5,
            s=28,
            alpha=0.85,
            label=species
        )

    # 사용자가 입력한 데이터: 노란색 별
    ax.scatter(
        petal_length,
        petal_width,
        marker="*",
        s=300,
        color="#FFD700",
        edgecolors="black",
        linewidths=1.2,
        zorder=10,
        label="Your input"
    )

    predicted_species = model.predict(input_data)[0]

    ax.set_title(
        f"{name}\nPrediction: {predicted_species}",
        fontsize=12
    )
    ax.set_xlabel("Petal length (cm)")
    ax.grid(
        True,
        linestyle="--",
        alpha=0.25
    )

axes[0].set_ylabel("Petal width (cm)")

# 범례는 첫 번째 그래프에만 표시
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles,
    labels,
    loc="lower center",
    ncol=min(len(labels), 4),
    bbox_to_anchor=(0.5, -0.03),
    frameon=False
)

fig.tight_layout(rect=[0, 0.12, 1, 1])
st.pyplot(fig, use_container_width=True)
plt.close(fig)

# --------------------------------------------------
# 10. 작동 원리 설명
# --------------------------------------------------
st.subheader("🧠 세 알고리즘의 작동 원리")

with st.expander("1. KNN — 가까운 이웃을 살펴보기", expanded=True):
    st.write(
        """
        1. 입력한 꽃잎 길이와 너비를 데이터의 점들과 비교합니다.
        2. 입력값과 거리가 가까운 데이터 5개를 찾습니다.
        3. 그 이웃들에서 가장 많이 나타난 품종을 예측합니다.

        **그래프에서 볼 점:** 가까운 데이터가 어느 품종인지에 따라
        배경색이 달라집니다. 주변 데이터가 바뀌는 곳에서 경계가
        달라질 수 있습니다.
        """
    )

with st.expander("2. 결정 트리 — 질문을 따라 분류하기"):
    st.write(
        """
        1. 꽃잎 길이와 너비를 기준으로 데이터를 나눌 조건을 찾습니다.
        2. 조건을 차례로 적용해 데이터가 여러 영역으로 나뉩니다.
        3. 도달한 영역에서 학습된 품종을 예측합니다.

        **그래프에서 볼 점:** 조건별로 영역을 나누기 때문에
        배경색의 경계가 계단처럼 직선으로 나타날 수 있습니다.
        """
    )

with st.expander("3. 랜덤 포레스트 — 여러 결정 트리의 의견 모으기"):
    st.write(
        """
        1. 학습 데이터와 특징을 다르게 활용해 여러 결정 트리를 만듭니다.
        2. 각 트리가 입력값의 품종을 예측합니다.
        3. 여러 트리의 예측을 모아 최종 품종을 결정합니다.

        **그래프에서 볼 점:** 여러 트리의 결과가 합쳐지므로
        하나의 결정 트리와 분류 영역이 다르게 나타날 수 있습니다.
        """
    )

# --------------------------------------------------
# 11. 정확도 비교 설명
# --------------------------------------------------
st.subheader("📈 정확도 비교")

accuracy_df = pd.DataFrame(
    {
        "알고리즘": list(accuracy_results.keys()),
        "테스트 정확도 (%)": [
            round(value * 100, 1)
            for value in accuracy_results.values()
        ],
    }
)

st.bar_chart(
    accuracy_df.set_index("알고리즘"),
    y="테스트 정확도 (%)"
)

best_algorithm = max(
    accuracy_results,
    key=accuracy_results.get
)

st.info(
    f"이번 테스트 데이터에서 가장 높은 정확도를 보인 알고리즘은 "
    f"**{best_algorithm}**이며, 정확도는 "
    f"**{accuracy_results[best_algorithm] * 100:.1f}%**입니다."
)

st.caption(
    "정확도는 데이터를 80% 학습용, 20% 테스트용으로 나누어 "
    "계산했습니다. 데이터 분할 방식에 따라 결과가 달라질 수 있습니다. "
    "예측 확률은 모델이 계산한 값이며, 실제 정답일 가능성을 "
    "완벽하게 보장하지는 않습니다."
)

# --------------------------------------------------
# 12. 원본 데이터 확인
# --------------------------------------------------
with st.expander("📄 붓꽃 데이터 확인하기"):
    st.write(f"전체 데이터 수: {len(df)}개")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("품종별 데이터 수")
    st.dataframe(
        df["품종"].value_counts().rename("데이터 수"),
        use_container_width=True
    )
