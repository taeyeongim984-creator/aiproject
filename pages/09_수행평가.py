
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="카페 메뉴 짝꿍 추천 ☕",
    page_icon="☕",
    layout="wide",
)

st.title("☕ 카페 메뉴 짝꿍 추천")
st.subheader("오늘은 어떤 카페에서 뭐 먹지? 🍰")
st.write(
    "좋아하는 카페를 고르면 음료와 디저트 메뉴를 살펴보고, "
    "각 메뉴에 어울리는 짝꿍 메뉴까지 추천해 줄게! ✨"
)

# --------------------------------------------------
# 2. CSV 파일 경로
#    현재 py 파일의 상위 폴더에서 CSV 찾기
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_CANDIDATES = [
    BASE_DIR / "franchise_drink_dessert_top3_sources_hollys (1).csv",
    BASE_DIR / "franchise_drink_dessert_top3_sources_hollys.csv",
]

CSV_PATH = next(
    (path for path in CSV_CANDIDATES if path.exists()),
    None,
)

# --------------------------------------------------
# 3. CSV 불러오기
# --------------------------------------------------
@st.cache_data
def load_data(file_path):
    # utf-8-sig로 읽고, 필요한 경우 cp949도 시도
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="cp949")

    required_columns = [
        "프랜차이즈",
        "구분",
        "순위",
        "메뉴명",
        "데이터기간",
        "순위기준",
        "출처",
        "출처URL",
        "비고",
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            "CSV에 필요한 열이 없습니다: " + ", ".join(missing)
        )

    df["순위"] = pd.to_numeric(df["순위"], errors="coerce")
    df["메뉴명"] = df["메뉴명"].fillna("").astype(str).str.strip()
    df["프랜차이즈"] = df["프랜차이즈"].fillna("").astype(str).str.strip()
    df["구분"] = df["구분"].fillna("").astype(str).str.strip()

    df = df[
        (df["메뉴명"] != "")
        & (df["프랜차이즈"] != "")
    ].copy()

    return df


# --------------------------------------------------
# 4. 메뉴 짝꿍 추천 사전
#    판매 순위가 아니라 맛의 조합을 고려한 추천
# --------------------------------------------------
DRINK_PAIRS = {
    "아메리카노": ("🍰", "치즈케이크", "깔끔한 커피와 고소한 치즈의 조합!"),
    "카페 아메리카노": ("🍰", "치즈케이크", "깔끔한 커피와 고소한 치즈의 조합!"),
    "카페라떼": ("🥐", "크루아상", "부드러운 우유 커피와 버터 풍미가 잘 어울려!"),
    "카페 라떼": ("🥐", "크루아상", "부드러운 우유 커피와 버터 풍미가 잘 어울려!"),
    "바닐라라떼": ("🍪", "초코 쿠키", "달콤한 바닐라와 초콜릿의 만남!"),
    "바닐라 딜라이트": ("🍪", "초코 쿠키", "달콤한 커피와 바삭한 쿠키의 조합!"),
    "자몽 허니 블랙 티": ("🍋", "레몬 케이크", "상큼한 과일 향이 디저트와 잘 어울려!"),
    "수박 주스": ("🥪", "담백한 샌드위치", "시원한 과일 주스와 담백한 한 끼!"),
    "말차크림라떼": ("🍫", "초코 브라우니", "쌉싸름한 말차와 진한 초콜릿의 조합!"),
    "메가베리 아사이볼": ("🥜", "견과류 쿠키", "상큼한 과일과 고소한 식감의 조화!"),
}

DESSERT_PAIRS = {
    "블루베리 마블 치즈 케이크": (
        "☕", "아메리카노", "달콤하고 진한 케이크를 깔끔하게 마무리해 줘."
    ),
    "레이디핑거 티라미수 케이크": (
        "☕", "카페 아메리카노", "커피 향이 티라미수의 풍미를 살려 줘."
    ),
    "바스크 초코 치즈 케이크": (
        "🥛", "카페라떼", "진한 초콜릿과 부드러운 우유의 조합!"
    ),
    "스트로베리 초콜릿 생크림(스초생)": (
        "☕", "아메리카노", "달콤한 딸기 생크림과 커피의 균형!"
    ),
    "떠먹는 아이스박스": (
        "🥛", "카페라떼", "크리미한 디저트와 부드러운 라떼!"
    ),
    "사라다빵": (
        "🥤", "아메리카노", "든든한 빵과 깔끔한 음료를 함께!"
    ),
    "모카번": (
        "☕", "아메리카노", "고소하고 달콤한 빵에 커피 한 잔!"
    ),
    "콘치즈쫀득볼": (
        "🥤", "아이스티", "고소한 콘치즈와 상큼한 음료의 조합!"
    ),
    "베리베리 딸기 요거트": (
        "🍵", "허브티", "상큼한 딸기와 산뜻한 차를 함께!"
    ),
    "스트로 베리머치 라운드": (
        "☕", "아메리카노", "딸기의 달콤함과 커피의 쌉싸름함!"
    ),
    "딸기 초코 쏘스윗박스": (
        "☕", "아메리카노", "초콜릿과 딸기의 단맛을 커피가 잡아 줘!"
    ),
    "메가베리 아사이볼": (
        "🥤", "레몬 에이드", "과일의 상큼함을 더해 주는 조합!"
    ),
    "팥빙 젤라또 파르페": (
        "☕", "아메리카노", "달콤하고 시원한 디저트와 깔끔한 커피!"
    ),
    "망빙 파르페": (
        "🍵", "아이스티", "달콤한 망고와 시원한 차의 조합!"
    ),
}


def suggest_drink_pair(menu):
    """음료에 어울리는 디저트 추천."""
    if menu in DRINK_PAIRS:
        emoji, name, reason = DRINK_PAIRS[menu]
        return emoji, name, reason

    if any(word in menu for word in ["티", "주스", "에이드", "아사이"]):
        return "🍰", "과일 케이크", "상큼한 음료와 부드러운 케이크를 함께!"
    if any(word in menu for word in ["라떼", "모카", "초콜릿"]):
        return "🍪", "쿠키", "달콤하고 고소한 맛을 함께 즐겨 봐!"
    return "🥐", "크루아상", "담백한 베이커리와 함께 즐겨 봐!"


def suggest_dessert_pair(menu):
    """디저트에 어울리는 음료 추천."""
    if menu in DESSERT_PAIRS:
        emoji, name, reason = DESSERT_PAIRS[menu]
        return emoji, name, reason

    if any(word in menu for word in ["딸기", "베리", "망고", "과일"]):
        return "🍵", "허브티", "과일의 상큼함을 살려 주는 산뜻한 차!"
    if any(word in menu for word in ["초코", "초콜릿", "브라우니"]):
        return "☕", "아메리카노", "진한 단맛과 커피의 조합!"
    if any(word in menu for word in ["치즈", "케이크", "티라미수"]):
        return "☕", "아메리카노", "디저트의 풍미를 살려 주는 깔끔한 커피!"
    return "🥤", "아이스티", "달콤한 디저트와 시원한 음료를 함께!"


# --------------------------------------------------
# 5. 순위 표시용 함수
# --------------------------------------------------
def get_top_menus(data, category):
    """
    공개된 순위가 있으면 순위순으로 표시.
    순위 미공개 메뉴는 별도 표시하며 임의로 순위를 매기지 않음.
    """
    subset = data[data["구분"] == category].copy()

    ranked = (
        subset[subset["순위"].notna()]
        .sort_values(["순위", "메뉴명"])
        .drop_duplicates(subset=["메뉴명"])
    )

    unranked = (
        subset[subset["순위"].isna()]
        .drop_duplicates(subset=["메뉴명"])
    )

    # 실제 순위가 공개된 메뉴 최대 3개
    result = []

    for _, row in ranked.head(3).iterrows():
        result.append({
            "메뉴명": row["메뉴명"],
            "표시순위": f"{int(row['순위'])}위",
            "행": row,
        })

    # 공개된 순위가 3개보다 적을 때는 나머지를
    # '순위 미공개'로 표시해 참고 메뉴로 보여 줌
    remaining = 3 - len(result)

    if remaining > 0:
        already_shown = {item["메뉴명"] for item in result}
        candidates = unranked[
            ~unranked["메뉴명"].isin(already_shown)
        ]

        for _, row in candidates.head(remaining).iterrows():
            result.append({
                "메뉴명": row["메뉴명"],
                "표시순위": "순위 미공개",
                "행": row,
            })

    return result


# --------------------------------------------------
# 6. 데이터 불러오기
# --------------------------------------------------
if CSV_PATH is None:
    st.error("CSV 파일을 찾을 수 없어! 😢")
    st.write("다음 위치에 CSV 파일이 있는지 확인해 줘.")
    st.code(str(BASE_DIR))
    st.write(
        "CSV 파일을 py 파일이 들어 있는 page 폴더의 "
        "바로 위 폴더에 넣어 줘."
    )
    st.stop()

try:
    df = load_data(CSV_PATH)
except Exception as error:
    st.error(f"CSV 파일을 읽는 중 문제가 발생했어: {error}")
    st.stop()

if df.empty:
    st.warning("CSV에 표시할 메뉴 데이터가 없어.")
    st.stop()

# --------------------------------------------------
# 7. 카페 선택
# --------------------------------------------------
st.divider()
st.markdown("### 🏪 어떤 카페를 골라 볼까?")

brands = sorted(df["프랜차이즈"].unique().tolist())

selected_brand = st.selectbox(
    "카페 브랜드 선택",
    brands,
    help="CSV에 들어 있는 카페만 선택할 수 있어.",
)

brand_data = df[df["프랜차이즈"] == selected_brand].copy()

st.success(f"🎉 {selected_brand} 메뉴를 살펴볼게!")

# --------------------------------------------------
# 8. 메뉴 순위와 짝꿍 메뉴 표시
# --------------------------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.markdown("## 🧋 음료 메뉴")
    st.caption("공개된 판매 순위를 우선으로 보여 줘.")

    drinks = get_top_menus(brand_data, "음료")

    if not drinks:
        st.info("등록된 음료 데이터가 없어.")
    else:
        for item in drinks:
            menu = item["메뉴명"]
            emoji, pair_name, reason = suggest_drink_pair(menu)

            with st.container(border=True):
                st.markdown(f"### 🏅 {item['표시순위']} · {menu}")
                st.markdown("**🍰 추천 짝꿍 디저트**")
                st.markdown(f"{emoji} **{pair_name}**")
                st.write(reason)

                row = item["행"]
                st.caption(
                    f"자료: {row['데이터기간']} · "
                    f"{row['순위기준']}"
                )
                if pd.notna(row["비고"]) and str(row["비고"]).strip():
                    st.caption(f"참고: {row['비고']}")

                if pd.notna(row["출처URL"]) and str(row["출처URL"]).startswith("http"):
                    st.markdown(f"[자료 출처 보기 ↗]({row['출처URL']})")

with right_col:
    st.markdown("## 🍰 디저트 메뉴")
    st.caption("순위가 확인되지 않은 메뉴는 따로 표시해.")

    desserts = get_top_menus(brand_data, "디저트")

    if not desserts:
        st.info("등록된 디저트 데이터가 없어.")
    else:
        for item in desserts:
            menu = item["메뉴명"]
            emoji, pair_name, reason = suggest_dessert_pair(menu)

            with st.container(border=True):
                st.markdown(f"### 🏅 {item['표시순위']} · {menu}")
                st.markdown("**☕ 추천 짝꿍 음료**")
                st.markdown(f"{emoji} **{pair_name}**")
                st.write(reason)

                row = item["행"]
                st.caption(
                    f"자료: {row['데이터기간']} · "
                    f"{row['순위기준']}"
                )
                if pd.notna(row["비고"]) and str(row["비고"]).strip():
                    st.caption(f"참고: {row['비고']}")

                if pd.notna(row["출처URL"]) and str(row["출처URL"]).startswith("http"):
                    st.markdown(f"[자료 출처 보기 ↗]({row['출처URL']})")

# --------------------------------------------------
# 9. 안내 및 데이터 전체 보기
# --------------------------------------------------
st.divider()

st.markdown("### 💡 이용할 때 참고해 줘!")
st.info(
    "🏅 숫자로 표시된 순위는 CSV에 기록된 자료를 기준으로 해. "
    "‘순위 미공개’는 인기 메뉴나 공식 메뉴로 확인됐지만 "
    "정확한 판매 순위를 확인할 수 없는 메뉴야. "
    "짝꿍 메뉴는 맛의 조합을 고려한 추천이며 공식 판매 순위가 아니야."
)

with st.expander("📚 선택한 카페의 데이터와 출처 전체 보기"):
    display_df = brand_data[
        [
            "구분",
            "순위",
            "메뉴명",
            "데이터기간",
            "순위기준",
            "출처",
            "출처URL",
            "비고",
        ]
    ].copy()

    display_df["순위"] = display_df["순위"].apply(
        lambda value: f"{int(value)}위"
        if pd.notna(value)
        else "순위 미공개"
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption("☕ 오늘의 카페 메뉴 선택에 도움이 되길 바라! 맛있게 즐겨 봐 🍀")
