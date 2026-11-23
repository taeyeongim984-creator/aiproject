
# ------------------------------------
# 6. 깔끔한 산점도 그리기 (한글 깨짐 방지)
# ------------------------------------

st.subheader("📊 꽃잎 길이와 너비의 관계")
st.write("노란색 별은 사용자가 입력한 꽃잎의 크기를 나타냅니다.")

# 그래프 내부에서는 한글 대신 영어 사용
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

# 품종별 데이터 표시
colors = ["#4285F4", "#34A853", "#EA4335"]

for species, color in zip(sorted(df["품종"].unique()), colors):
    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎 길이"],
        subset["꽃잎 너비"],
        label=str(species),
        color=color,
        s=55,
        alpha=0.8,
        edgecolors="white",
        linewidths=0.5
    )

# 사용자 입력 위치: 노란색 별
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

# 영어 제목 및 축 이름으로 한글 글꼴 문제 방지
ax.set_title(
    "Iris Petal Length vs Petal Width",
    fontsize=15,
    fontweight="bold",
    pad=15
)
ax.set_xlabel("Petal Length (cm)", fontsize=12, labelpad=8)
ax.set_ylabel("Petal Width (cm)", fontsize=12, labelpad=8)

# 데이터 범위에 맞춘 축 설정
ax.set_xlim(length_min - 0.3, length_max + 0.3)
ax.set_ylim(width_min - 0.15, width_max + 0.15)

# 깔끔한 배경과 격자
ax.set_facecolor("#FAFAFA")
ax.grid(
    True,
    linestyle="--",
    linewidth=0.6,
    alpha=0.3
)
ax.set_axisbelow(True)

# 범례와 테두리 정리
ax.legend(
    title="Species",
    frameon=True,
    fontsize=9,
    loc="best"
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
