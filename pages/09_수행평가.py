
from pathlib import Path

import pandas as pd
import streamlit as st

# =========================================
# 1. 페이지 설정
# =========================================
st.set_page_config(
    page_title="카페 메뉴 짝꿍 추천",
    page_icon="☕",
    layout="wide",
)

st.title("☕ 오늘의 카페 메뉴 짝꿍")
st.subheader("음료도 디저트도 맛있게 골라 보자! 🍰")
st.write(
    "카페를 고르면 음료와 디저트 메뉴를 최대 3개씩 보여 줄게. "
    "각 메뉴와 잘 어울리는 짝꿍도 추천해 줄게! 🧋✨"
)

# =========================================
# 2. 파일 경로
# py 파일: page/09_카페메뉴추천.py
# CSV: page 폴더의 상위 폴더
# =========================================
PROJECT_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = PROJECT_DIR / "수행평가_인공지능(1).csv"

# =========================================
# 3. CSV 읽기
# =========================================
@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    required_columns = [
        "프랜차이즈",
        "구분",
        "순위",
        "메뉴명",
        "데이터기간",
        "순위기준",
        "출처",
        "출처URL",
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            "CSV에 다음 열이 없어: " + ", ".join(missing)
        )

    for col in required_columns:
        data[col] = data[col].fillna("").astype(str).str.strip()

    data["순위"] = pd.to_numeric(data["순위"], errors="coerce")

    data = data[
        (data["프랜차이즈"] != "")
        & (data["메뉴명"] != "")
    ].copy()

    return data


# 파일이 있는지 확인
if not CSV_PATH.is_file():
    st.error("CSV 파일을 찾지 못했어! 😢")
    st.write("코드에서 찾고 있는 위치:")
    st.code(str(CSV_PATH))
    st.write(
        "CSV 파일이 page 폴더 안이 아니라 "
        "page 폴더의 상위 폴더에 있는지 확인해 줘."
    )
    st.stop()

try:
    df = load_data(CSV_PATH)
except Exception as e:
    st.error(f"CSV 파일을 읽을 수 없어: {e}")
    st.stop()

if df.empty:
    st.warning("CSV에 표시할 메뉴가 없어. 파일 내용을 확인해 줘!")
    st.stop()

# =========================================
# 4. 음료에 어울리는 디저트 추천
# =========================================
def recommend_dessert(drink):
    name = drink.replace(" ", "").lower()

    if "아메리카노" in name:
        return "🍰 치즈케이크", "깔끔한 커피와 고소한 치즈의 조합!"

    if any(word in name for word in ["라떼", "모카", "초콜릿"]):
        return "🍪 초코 쿠키", "부드럽고 달콤한 음료와 바삭한 쿠키!"

    if any(word in name for word in ["티", "에이드", "주스", "아사이"]):
        return "🥐 담백한 베이커리", "상큼한 음료와 담백한 빵을 함께!"

    return "🧁 미니 케이크", "음료와 달콤한 한입 디저트를 즐겨 봐!"


# =========================================
# 5. 디저트에 어울리는 음료 추천
# =========================================
def recommend_drink(dessert):
    name = dessert.replace(" ", "").lower()

    if any(word in name for word in ["딸기", "베리", "망고", "과일"]):
        return "🍵 산뜻한 차", "과일의 상큼함을 살려 주는 깔끔한 차!"

    if any(word in name for word in ["초코", "초콜릿", "브라우니"]):
        return "☕ 아메리카노", "초콜릿의 달콤함과 커피의 쌉싸름함!"

    if any(word in name for word in ["치즈", "케이크", "티라미수"]):
        return "☕ 아메리카노", "커피가 케이크의 풍미를 살려 줘!"

    if any(word in name for word in ["빵", "번", "샌드위치"]):
        return "🥛 카페라떼", "고소한 빵과 부드러운 우유 커피!"

    return "🧋 아이스티", "달콤한 디저트와 시원한 음료를 함께!"


# =========================================
# 6. 순위 표시
# =========================================
def rank_label(row):
    criteria = str(row["순위기준"])
    rank = row["순위"]

    if "정확한 순위 미공개" in criteria:
        return "순위 미공개"

    if "판매 순위 아님" in criteria:
        return "공식 메뉴 · 판매 순위 아님"

    if pd.isna(rank):
        return "순위 미공개"

    return f"{int(rank)}위"


def source_note(row):
    criteria = str(row["순위기준"])

    if "정확한 순위 미공개" in criteria:
        return "ℹ️ 인기 메뉴로 언급됐지만 정확한 판매 순위는 공개되지 않았어."

    if "판매 순위 아님" in criteria:
        return "ℹ️ 공식 메뉴 자료이며 판매 순위는 아니야."

    return f"📅 자료 기간: {row['데이터기간']}"


def show_source(row):
    if row["출처"]:
        st.caption(f"자료 출처: {row['출처']}")

    url = str(row["출처URL"]).strip()

    if url.startswith(("https://", "http://")):
        st.markdown(f"[📎 출처 확인하기]({url})")


# =========================================
# 7. 카페 선택
# =========================================
st.divider()
st.markdown("### 🏪 어떤 카페를 골라 볼까?")

brands = sorted(df["프랜차이즈"].unique().tolist())

selected_brand = st.selectbox(
    "프랜차이즈 카페 선택",
    brands,
)

brand_df = df[df["프랜차이즈"] == selected_brand].copy()

st.success(f"🎉 {selected_brand} 메뉴를 살펴보자!")

# =========================================
# 8. 카테고리별 메뉴 최대 3개
# =========================================
def get_top_three(data, category):
    result = data[data["구분"] == category].copy()

    result = result.sort_values(
        by=["순위", "메뉴명"],
        na_position="last",
    )

    result = result.drop_duplicates(subset=["메뉴명"])

    return result.head(3)


drinks = get_top_three(brand_df, "음료")
desserts = get_top_three(brand_df, "디저트")

left, right = st.columns(2)

# =========================================
# 9. 음료 메뉴
# =========================================
with left:
    st.markdown("## 🧋 음료 TOP 3")

    if drinks.empty:
        st.info("이 카페의 음료 데이터가 없어.")
    else:
        for _, row in drinks.iterrows():
            menu = row["메뉴명"]
            pair, reason = recommend_dessert(menu)

            with st.container(border=True):
                st.markdown(
                    f"### 🏅 {rank_label(row)} · {menu}"
                )
                st.markdown("**🍰 어울리는 디저트**")
                st.markdown(f"### {pair}")
                st.write(reason)
                st.caption(source_note(row))
                show_source(row)

# =========================================
# 10. 디저트 메뉴
# =========================================
with right:
    st.markdown("## 🍰 디저트 TOP 3")

    if desserts.empty:
        st.info("이 카페의 디저트 데이터가 없어.")
    else:
        for _, row in desserts.iterrows():
            menu = row["메뉴명"]
            pair, reason = recommend_drink(menu)

            with st.container(border=True):
                st.markdown(
                    f"### 🏅 {rank_label(row)} · {menu}"
                )
                st.markdown("**☕ 어울리는 음료**")
                st.markdown(f"### {pair}")
                st.write(reason)
                st.caption(source_note(row))
                show_source(row)

# =========================================
# 11. 원본 데이터 확인
# =========================================
st.divider()

with st.expander("📚 선택한 카페의 원본 자료 보기"):
    st.dataframe(
        brand_df[
            [
                "프랜차이즈",
                "구분",
                "순위",
                "메뉴명",
                "데이터기간",
                "순위기준",
                "출처",
                "출처URL",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.info(
    "💡 메뉴 순위는 CSV에 기록된 자료를 기준으로 표시해. "
    "카페마다 조사 시기와 순위 기준이 다를 수 있어. "
    "정확한 순위가 공개되지 않은 메뉴는 순위 미공개로 표시하고, "
    "짝꿍 메뉴는 맛 조합을 고려해 추천해."
)

st.markdown("### 🍀 오늘도 맛있는 카페 타임 보내!")
