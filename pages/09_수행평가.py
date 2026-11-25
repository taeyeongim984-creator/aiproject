
from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="카페 메뉴 짝꿍 추천",
    page_icon="☕",
    layout="wide",
)

st.title("☕ 오늘의 카페 메뉴 짝꿍")
st.subheader("음료도 디저트도 맛있게 골라 보자! 🍰")
st.write(
    "카페를 선택하면 음료와 디저트 메뉴를 각각 3개씩 보여 줄게. "
    "각 메뉴에 어울리는 짝꿍 메뉴도 확인해 봐! 🧋✨"
)

# ==========================================
# 2. 파일 경로 설정
# py 파일: page/09_카페메뉴추천.py
# CSV 파일: 프로젝트 상위 폴더
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "수행평가_인공지능(1).csv"

# ==========================================
# 3. CSV 데이터 불러오기
# ==========================================
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(file_path, encoding="cp949")

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

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV에 필요한 열이 없어: "
            + ", ".join(missing_columns)
        )

    # 빈칸과 자료형 정리
    for column in required_columns:
        data[column] = data[column].fillna("").astype(str).str.strip()

    data["순위"] = pd.to_numeric(data["순위"], errors="coerce")

    data = data[
        (data["프랜차이즈"] != "")
        & (data["메뉴명"] != "")
    ].copy()

    return data


# 파일이 없으면 오류 안내
if not CSV_PATH.exists():
    st.error("CSV 파일을 찾을 수 없어! 😢")
    st.write("CSV 파일을 page 폴더의 상위 폴더에 넣어 줘.")
    st.write("코드에서 찾고 있는 경로:")
    st.code(str(CSV_PATH))
    st.stop()

try:
    df = load_data(CSV_PATH)
except Exception as error:
    st.error(f"CSV 파일을 읽는 중 문제가 발생했어: {error}")
    st.stop()

if df.empty:
    st.warning("CSV에 표시할 메뉴가 없어. 파일 내용을 확인해 줘!")
    st.stop()


# ==========================================
# 4. 음료에 어울리는 디저트 추천
# 맛 조합 추천이며 판매 순위가 아님
# ==========================================
def recommend_dessert(drink):
    name = drink.replace(" ", "").lower()

    if any(word in name for word in ["아메리카노", "블랙커피"]):
        return (
            "🍰 치즈케이크",
            "깔끔한 커피와 고소하고 부드러운 치즈의 조합!"
        )

    if any(word in name for word in ["라떼", "모카", "초콜릿"]):
        return (
            "🍪 초코 쿠키",
            "부드럽고 달콤한 음료에 바삭한 쿠키를 곁들여 봐!"
        )

    if any(word in name for word in ["티", "에이드", "주스", "아사이"]):
        return (
            "🥐 담백한 베이커리",
            "상큼한 음료와 담백한 빵을 함께 즐겨 봐!"
        )

    return (
        "🧁 미니 케이크",
        "좋아하는 음료에 달콤한 한입 디저트를 곁들여 봐!"
    )


# ==========================================
# 5. 디저트에 어울리는 음료 추천
# ==========================================
def recommend_drink(dessert):
    name = dessert.replace(" ", "").lower()

    if any(word in name for word in ["딸기", "베리", "망고", "과일"]):
        return (
            "🍵 산뜻한 차",
            "과일의 상큼함을 살려 주는 깔끔한 차!"
        )

    if any(word in name for word in ["초코", "초콜릿", "브라우니"]):
        return (
            "☕ 아메리카노",
            "초콜릿의 달콤함과 커피의 쌉싸름함이 잘 어울려!"
        )

    if any(word in name for word in ["치즈", "케이크", "티라미수"]):
        return (
            "☕ 아메리카노",
            "커피의 깔끔한 맛이 케이크의 풍미를 살려 줘!"
        )

    if any(word in name for word in ["빵", "번", "샌드위치"]):
        return (
            "🥛 카페라떼",
            "고소한 빵과 부드러운 우유 커피의 조합!"
        )

    return (
        "🧋 아이스티",
        "달콤한 디저트와 시원한 음료를 함께 즐겨 봐!"
    )


# ==========================================
# 6. 순위와 출처 안내
# ==========================================
def get_rank_label(row):
    criteria = str(row["순위기준"])

    if "정확한 순위 미공개" in criteria:
        return "순위 미공개"

    if "판매 순위 아님" in criteria:
        return "공식 메뉴 · 판매 순위 아님"

    return (
        f"{int(row['순위'])}위"
        if pd.notna(row["순위"])
        else "순위 미공개"
    )


def get_source_note(row):
    criteria = str(row["순위기준"])
    period = str(row["데이터기간"])

    if "정확한 순위 미공개" in criteria:
        return "ℹ️ 인기 메뉴로 언급됐지만 정확한 판매 순위는 공개되지 않았어."

    if "판매 순위 아님" in criteria:
        return "ℹ️ 공식 메뉴 자료이며 판매 순위를 의미하지 않아."

    return f"📅 자료 기간: {period}"


def show_source(row):
    source = str(row["출처"]).strip()
    url = str(row["출처URL"]).strip()

    if source:
        st.caption(f"자료 출처: {source}")

    if url.startswith("https://") or url.startswith("http://"):
        st.markdown(f"[📎 출처 자료 확인하기]({url})")


# ==========================================
# 7. 카페 선택
# ==========================================
st.divider()
st.markdown("### 🏪 어떤 카페를 골라 볼까?")

brands = sorted(df["프랜차이즈"].unique().tolist())

selected_brand = st.selectbox(
    "프랜차이즈 카페 선택",
    brands,
)

brand_df = df[df["프랜차이즈"] == selected_brand].copy()

st.success(f"🎉 {selected_brand} 메뉴를 골라 봤어!")

# ==========================================
# 8. 음료와 디저트 메뉴 각각 최대 3개
# ==========================================
def get_top_three(data, category):
    items = data[data["구분"] == category].copy()

    items = items.sort_values(
        by=["순위", "메뉴명"],
        na_position="last",
    )

    # 같은 메뉴가 중복되면 한 번만 표시
    items = items.drop_duplicates(subset=["메뉴명"])

    return items.head(3)


drink_df = get_top_three(brand_df, "음료")
dessert_df = get_top_three(brand_df, "디저트")

left, right = st.columns(2)

# ==========================================
# 9. 음료 TOP 3와 추천 디저트
# ==========================================
with left:
    st.markdown("## 🧋 음료 메뉴 TOP 3")

    if drink_df.empty:
        st.info("등록된 음료 자료가 없어.")
    else:
        for _, row in drink_df.iterrows():
            menu = row["메뉴명"]
            rank = get_rank_label(row)
            pair, reason = recommend_dessert(menu)

            with st.container(border=True):
                st.markdown(f"### 🏅 {rank} · {menu}")
                st.markdown("**🍰 찰떡 궁합 디저트**")
                st.markdown(f"### {pair}")
                st.write(reason)
                st.caption(get_source_note(row))
                show_source(row)

# ==========================================
# 10. 디저트 TOP 3와 추천 음료
# ==========================================
with right:
    st.markdown("## 🍰 디저트 메뉴 TOP 3")

    if dessert_df.empty:
        st.info("등록된 디저트 자료가 없어.")
    else:
        for _, row in dessert_df.iterrows():
            menu = row["메뉴명"]
            rank = get_rank_label(row)
            pair, reason = recommend_drink(menu)

            with st.container(border=True):
                st.markdown(f"### 🏅 {rank} · {menu}")
                st.markdown("**☕ 찰떡 궁합 음료**")
                st.markdown(f"### {pair}")
                st.write(reason)
                st.caption(get_source_note(row))
                show_source(row)

# ==========================================
# 11. 원본 자료 확인
# ==========================================
st.divider()

with st.expander("📚 선택한 카페의 원본 데이터 보기"):
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
    "💡 순위는 CSV에 기록된 자료를 기준으로 표시해. "
    "카페마다 조사 시기와 순위 기준이 다를 수 있어. "
    "순위가 공개되지 않았거나 공식 메뉴만 확인된 경우에는 "
    "임의로 판매 순위를 만들지 않아. "
    "짝꿍 메뉴는 맛 조합을 고려한 추천이야."
)

st.markdown("### 🍀 오늘도 맛있는 카페 타임 보내!")
