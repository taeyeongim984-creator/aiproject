
import streamlit as st

st.set_page_config(
    page_title="MBTI 책·영화 탐험",
    page_icon="📚",
    layout="centered"
)

# -----------------------------------
# 1. 책 데이터
# -----------------------------------

books = [
    {
        "title": "아몬드",
        "year": 2017,
        "country": "한국",
        "genres": ["소설", "성장소설"],
        "tags": ["감정", "성장", "공감", "위로"],
        "description": "감정을 이해하고 사람들과 관계를 맺는 과정에 관한 청소년 소설이에요.",
        "reason": "감정과 공감에 관해 생각해 보고 싶을 때 추천해요."
    },
    {
        "title": "불편한 편의점",
        "year": 2021,
        "country": "한국",
        "genres": ["소설", "힐링소설"],
        "tags": ["위로", "힐링", "일상", "공감"],
        "description": "편의점을 중심으로 다양한 사람들의 사연과 관계를 담았어요.",
        "reason": "복잡한 마음을 잠시 내려놓고 따뜻한 이야기를 읽고 싶을 때 좋아요."
    },
    {
        "title": "페인트",
        "year": 2019,
        "country": "한국",
        "genres": ["소설", "청소년소설"],
        "tags": ["성장", "가족", "선택", "공감"],
        "description": "가족과 선택의 의미를 새롭게 생각해 보게 하는 청소년 소설이에요.",
        "reason": "자신의 선택과 미래에 대해 고민하고 싶을 때 추천해요."
    },
    {
        "title": "체리새우: 비밀글입니다",
        "year": 2019,
        "country": "한국",
        "genres": ["소설", "청소년소설"],
        "tags": ["우정", "학교", "성장", "공감"],
        "description": "친구 관계와 자신의 모습을 고민하는 청소년의 이야기예요.",
        "reason": "친구 관계 때문에 고민할 때 공감하며 읽기 좋아요."
    },
    {
        "title": "시간을 파는 상점",
        "year": 2012,
        "country": "한국",
        "genres": ["소설", "청소년소설"],
        "tags": ["시간", "선택", "추리", "성장"],
        "description": "시간과 선택을 둘러싼 사건과 사람들의 이야기를 담았어요.",
        "reason": "선택의 의미와 사건의 단서를 따라가는 재미를 느낄 수 있어요."
    },
    {
        "title": "완득이",
        "year": 2008,
        "country": "한국",
        "genres": ["소설", "청소년소설"],
        "tags": ["성장", "가족", "우정", "희망"],
        "description": "한 청소년이 주변 사람들과 부딪치며 성장하는 이야기예요.",
        "reason": "성장 과정에서 만나는 어려움과 관계를 생각해 볼 수 있어요."
    },
    {
        "title": "어린 왕자",
        "year": 1943,
        "country": "해외",
        "genres": ["소설", "철학동화"],
        "tags": ["위로", "관계", "상상력", "삶"],
        "description": "여러 별을 여행하는 어린 왕자를 통해 관계와 삶의 의미를 살펴봐요.",
        "reason": "바쁜 일상에서 잠시 멈춰 삶의 의미를 생각하고 싶을 때 추천해요."
    },
    {
        "title": "모모",
        "year": 1973,
        "country": "해외",
        "genres": ["소설", "판타지"],
        "tags": ["시간", "위로", "상상력", "삶"],
        "description": "시간의 의미와 사람다운 삶에 관해 생각하게 하는 판타지 소설이에요.",
        "reason": "시간에 쫓기는 일상에서 무엇이 중요한지 돌아볼 수 있어요."
    },
    {
        "title": "나미야 잡화점의 기적",
        "year": 2012,
        "country": "해외",
        "genres": ["소설", "미스터리"],
        "tags": ["위로", "선택", "감동", "공감"],
        "description": "고민 상담 편지를 통해 여러 사람의 삶이 연결되는 이야기예요.",
        "reason": "고민과 선택, 사람 사이의 따뜻한 연결을 느끼고 싶을 때 좋아요."
    },
    {
        "title": "해리 포터와 마법사의 돌",
        "year": 1997,
        "country": "해외",
        "genres": ["소설", "판타지"],
        "tags": ["모험", "우정", "마법", "용기"],
        "description": "마법 학교에 입학한 소년이 새로운 세계와 비밀을 만나게 돼요.",
        "reason": "현실을 잠시 벗어나 신나는 모험과 우정을 즐기고 싶을 때 추천해요."
    },
    {
        "title": "슬램덩크",
        "year": 1990,
        "country": "일본",
        "genres": ["만화", "스포츠"],
        "tags": ["성장", "우정", "도전", "팀워크"],
        "description": "농구를 통해 도전과 팀워크를 배워 가는 청춘 만화예요.",
        "reason": "목표를 향해 노력하는 에너지를 얻고 싶을 때 좋아요."
    },
    {
        "title": "명탐정 코난",
        "year": 1994,
        "country": "일본",
        "genres": ["만화", "추리"],
        "tags": ["추리", "미스터리", "논리", "사건"],
        "description": "사건의 단서를 모아 진실을 찾아가는 추리 만화예요.",
        "reason": "추리와 논리적인 문제 해결을 좋아하는 사람에게 추천해요."
    },
    {
        "title": "유미의 세포들",
        "year": 2015,
        "country": "한국",
        "genres": ["만화", "일상"],
        "tags": ["감정", "공감", "일상", "성장"],
        "description": "주인공의 마음속 세포들을 통해 일상과 감정을 재미있게 보여 줘요.",
        "reason": "복잡한 감정을 유쾌하게 들여다보고 싶을 때 좋아요."
    },
    {
        "title": "마음의 소리",
        "year": 2006,
        "country": "한국",
        "genres": ["만화", "코미디"],
        "tags": ["웃음", "일상", "기분전환"],
        "description": "일상의 엉뚱한 상황을 유쾌하게 풀어낸 코미디 만화예요.",
        "reason": "가볍게 웃으며 기분을 전환하고 싶을 때 추천해요."
    }
]

# -----------------------------------
# 2. 영화 데이터
# -----------------------------------

movies = [
    {
        "title": "인사이드 아웃",
        "year": 2015,
        "country": "해외",
        "genres": ["애니메이션", "가족"],
        "tags": ["감정", "성장", "위로", "공감"],
        "description": "감정 캐릭터들을 통해 마음의 변화와 감정의 의미를 보여 줘요.",
        "reason": "내 감정을 이해하고 마음을 돌보는 방법을 생각해 볼 수 있어요."
    },
    {
        "title": "코코",
        "year": 2017,
        "country": "해외",
        "genres": ["애니메이션", "판타지"],
        "tags": ["가족", "음악", "감동", "꿈"],
        "description": "음악을 사랑하는 소년이 가족과 기억의 의미를 알아가는 이야기예요.",
        "reason": "가족의 의미와 꿈을 향한 도전을 생각해 보고 싶을 때 추천해요."
    },
    {
        "title": "소울",
        "year": 2020,
        "country": "해외",
        "genres": ["애니메이션", "판타지"],
        "tags": ["꿈", "위로", "삶", "힐링"],
        "description": "삶의 목적과 일상 속 작은 기쁨에 관해 생각하게 하는 영화예요.",
        "reason": "미래에 대한 고민이 많을 때 삶의 다양한 가치를 생각해 볼 수 있어요."
    },
    {
        "title": "주토피아",
        "year": 2016,
        "country": "해외",
        "genres": ["애니메이션", "코미디"],
        "tags": ["편견", "도전", "추리", "우정"],
        "description": "토끼 경찰과 여우가 도시의 사건을 조사하며 편견에 맞서요.",
        "reason": "편견을 넘어 서로 이해하는 과정과 도전 정신을 살펴볼 수 있어요."
    },
    {
        "title": "너의 이름은.",
        "year": 2016,
        "country": "일본",
        "genres": ["애니메이션", "판타지", "로맨스"],
        "tags": ["인연", "성장", "감동", "판타지"],
        "description": "서로 다른 곳에 사는 두 청소년에게 신비한 일이 일어나요.",
        "reason": "아름다운 영상과 신비로운 이야기를 즐기고 싶을 때 추천해요."
    },
    {
        "title": "센과 치히로의 행방불명",
        "year": 2001,
        "country": "일본",
        "genres": ["애니메이션", "판타지"],
        "tags": ["모험", "성장", "용기", "상상력"],
        "description": "낯선 세계에 들어간 소녀가 용기를 내어 성장하는 이야기예요.",
        "reason": "낯선 환경에서 성장하는 주인공을 만나고 싶을 때 좋아요."
    },
    {
        "title": "기생충",
        "year": 2019,
        "country": "한국",
        "genres": ["드라마", "스릴러"],
        "tags": ["사회", "계층", "미스터리"],
        "description": "두 가족의 관계를 통해 사회적 격차를 생각하게 하는 영화예요.",
        "reason": "사회 문제와 인간관계를 다양한 관점에서 생각할 수 있어요."
    },
    {
        "title": "국제시장",
        "year": 2014,
        "country": "한국",
        "genres": ["드라마", "역사"],
        "tags": ["가족", "역사", "희생", "감동"],
        "description": "한 인물의 삶을 통해 한국 현대사의 여러 장면을 보여 줘요.",
        "reason": "가족의 의미와 역사 속 사람들의 삶을 살펴볼 수 있어요."
    },
    {
        "title": "리틀 포레스트",
        "year": 2018,
        "country": "한국",
        "genres": ["드라마", "힐링"],
        "tags": ["힐링", "일상", "위로", "성장"],
        "description": "고향으로 돌아온 주인공이 음식과 일상 속에서 자신을 돌아봐요.",
        "reason": "복잡한 마음을 쉬게 하고 잔잔한 위로를 받고 싶을 때 추천해요."
    },
    {
        "title": "7번방의 선물",
        "year": 2013,
        "country": "한국",
        "genres": ["드라마", "코미디"],
        "tags": ["가족", "감동", "사랑"],
        "description": "가족의 사랑과 주변 사람들의 관계를 다룬 영화예요.",
        "reason": "가족과 사랑의 의미를 생각해 보고 싶을 때 좋아요."
    },
    {
        "title": "극한직업",
        "year": 2019,
        "country": "한국",
        "genres": ["코미디", "액션"],
        "tags": ["웃음", "팀워크", "기분전환"],
        "description": "잠복 수사를 하던 형사들이 예상 밖의 상황에 놓이게 돼요.",
        "reason": "신나게 웃으며 스트레스를 풀고 싶을 때 추천해요."
    },
    {
        "title": "월-E",
        "year": 2008,
        "country": "해외",
        "genres": ["애니메이션", "SF"],
        "tags": ["환경", "로봇", "사랑", "미래"],
        "description": "지구에 남겨진 로봇을 통해 환경과 미래를 생각하게 해요.",
        "reason": "환경 문제와 미래 사회에 관심이 있다면 재미있게 볼 수 있어요."
    },
    {
        "title": "인턴",
        "year": 2015,
        "country": "해외",
        "genres": ["코미디", "드라마"],
        "tags": ["직장", "우정", "성장", "소통"],
        "description": "새로운 직장에서 세대가 다른 두 사람이 서로를 이해해 가요.",
        "reason": "세대 간 소통과 새로운 도전을 생각해 볼 수 있어요."
    },
    {
        "title": "히든 피겨스",
        "year": 2016,
        "country": "해외",
        "genres": ["드라마", "역사"],
        "tags": ["과학", "도전", "성장", "꿈"],
        "description": "수학적 능력으로 우주 개발에 기여한 여성들의 이야기예요.",
        "reason": "꿈을 향한 노력과 과학 분야의 도전 정신을 느낄 수 있어요."
    },
    {
        "title": "스파이더맨: 뉴 유니버스",
        "year": 2018,
        "country": "해외",
        "genres": ["애니메이션", "액션"],
        "tags": ["성장", "용기", "도전", "우정"],
        "description": "새로운 영웅이 자신의 가능성을 발견하는 모험 이야기예요.",
        "reason": "자신만의 방식으로 성장하는 주인공에게서 용기를 얻을 수 있어요."
    },
    {
        "title": "마당을 나온 암탉",
        "year": 2011,
        "country": "한국",
        "genres": ["애니메이션", "가족"],
        "tags": ["성장", "용기", "가족", "감동"],
        "description": "자신의 삶을 선택하고 꿈을 향해 나아가는 암탉의 이야기예요.",
        "reason": "꿈과 선택, 사랑의 의미를 생각해 볼 수 있어요."
    }
]

# -----------------------------------
# 3. MBTI별 기본 추천 목록
# -----------------------------------

recommendations = {
    "ISTJ": {
        "books": ["명탐정 코난", "시간을 파는 상점"],
        "movies": ["히든 피겨스", "인턴"]
    },
    "ISFJ": {
        "books": ["불편한 편의점", "체리새우: 비밀글입니다"],
        "movies": ["코코", "7번방의 선물"]
    },
    "INFJ": {
        "books": ["어린 왕자", "아몬드"],
        "movies": ["소울", "인사이드 아웃"]
    },
    "INTJ": {
        "books": ["시간을 파는 상점", "명탐정 코난"],
        "movies": ["히든 피겨스", "기생충"]
    },
    "ISTP": {
        "books": ["슬램덩크", "명탐정 코난"],
        "movies": ["스파이더맨: 뉴 유니버스", "극한직업"]
    },
    "ISFP": {
        "books": ["어린 왕자", "유미의 세포들"],
        "movies": ["리틀 포레스트", "코코"]
    },
    "INFP": {
        "books": ["모모", "아몬드"],
        "movies": ["소울", "너의 이름은."]
    },
    "INTP": {
        "books": ["명탐정 코난", "해리 포터와 마법사의 돌"],
        "movies": ["히든 피겨스", "월-E"]
    },
    "ESTP": {
        "books": ["슬램덩크", "마음의 소리"],
        "movies": ["극한직업", "스파이더맨: 뉴 유니버스"]
    },
    "ESFP": {
        "books": ["마음의 소리", "슬램덩크"],
        "movies": ["코코", "극한직업"]
    },
    "ENFP": {
        "books": ["해리 포터와 마법사의 돌", "마당을 나온 암탉"],
        "movies": ["너의 이름은.", "주토피아"]
    },
    "ENTP": {
        "books": ["시간을 파는 상점", "유미의 세포들"],
        "movies": ["주토피아", "기생충"]
    },
    "ESTJ": {
        "books": ["슬램덩크", "페인트"],
        "movies": ["인턴", "히든 피겨스"]
    },
    "ESFJ": {
        "books": ["불편한 편의점", "완득이"],
        "movies": ["국제시장", "7번방의 선물"]
    },
    "ENFJ": {
        "books": ["완득이", "페인트"],
        "movies": ["코코", "인사이드 아웃"]
    },
    "ENTJ": {
        "books": ["페인트", "해리 포터와 마법사의 돌"],
        "movies": ["히든 피겨스", "스파이더맨: 뉴 유니버스"]
    }
}

# -----------------------------------
# 4. 단서 해석
# -----------------------------------

def matches_clue(item, clue):
    clue = clue.strip().lower()

    if not clue:
        return True

    # 연도 조건
    if "2010년 이후" in clue and item["year"] < 2010:
        return False

    if "2000년 이후" in clue and item["year"] < 2000:
        return False

    if "2020년 이후" in clue and item["year"] < 2020:
        return False

    # 국가 조건
    if "한국" in clue and item["country"] != "한국":
        return False

    if "일본" in clue and item["country"] != "일본":
        return False

    if "해외" in clue and item["country"] in ["한국", "일본"]:
        return False

    # 장르 조건
    genre_keywords = [
        "만화", "소설", "애니메이션", "코미디",
        "드라마", "스릴러", "판타지", "힐링", "추리"
    ]

    for genre in genre_keywords:
        if genre in clue:
            if genre not in item["genres"]:
                return False

    # 분위기 및 주제 조건
    keyword_map = {
        "마음을 추스": ["위로", "힐링", "감정", "성장", "감동"],
        "위로": ["위로", "힐링", "감정", "감동"],
        "힐링": ["힐링", "위로"],
        "기분 전환": ["기분전환", "웃음", "모험"],
        "웃긴": ["웃음", "기분전환"],
        "재미있는": ["웃음", "모험", "추리", "판타지"],
        "성장": ["성장"],
        "우정": ["우정", "팀워크"],
        "가족": ["가족"],
        "꿈": ["꿈", "도전"],
        "추리": ["추리", "미스터리", "사건"],
        "감동": ["감동", "가족", "공감", "위로"],
        "공감": ["공감", "감정", "위로"],
        "용기": ["용기", "도전"],
        "환경": ["환경", "미래"],
        "학교": ["학교", "성장", "우정"]
    }

    for keyword, tags in keyword_map.items():
        if keyword in clue:
            if not any(tag in item["tags"] for tag in tags):
                return False

    return True


# -----------------------------------
# 5. 화면 구성
# -----------------------------------

st.title("📚 MBTI 책·영화 탐험 🎬")

st.write(
    "안녕! 👋 나의 MBTI와 읽고 싶은 책·보고 싶은 영화의 단서를 입력하면 "
    "취향에 맞는 작품을 찾아볼 수 있어!"
)

st.info(
    "🧩 단서 예시: '2010년 이후 마음을 추스를 수 있는 책과 영화', "
    "'한국 소설', '재미있는 만화', '성장에 도움이 되는 이야기'"
)

mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
]

mbti = st.selectbox(
    "🌈 나의 MBTI를 골라 줘!",
    mbti_types
)

clue = st.text_area(
    "🔎 어떤 작품을 찾고 싶어?",
    placeholder="예: 2010년 이후 마음을 추스를 수 있는 책과 영화",
    help="연도, 국가, 장르, 분위기 등을 자유롭게 적어 줘."
)

if st.button("✨ 맞춤 작품 추천받기", use_container_width=True):

    st.session_state["last_mbti"] = mbti
    st.session_state["last_clue"] = clue
    st.session_state["show_result"] = True

if st.session_state.get("show_result", False):

    result_mbti = st.session_state["last_mbti"]
    result_clue = st.session_state["last_clue"]

    st.divider()
    st.header("🌟 " + result_mbti + " 맞춤 추천")

    # 책 추천
    st.subheader("📚 추천 책 2권")

    book_names = recommendations[result_mbti]["books"]
    matched_books = []

    for name in book_names:
        for book in books:
            if book["title"] == name and matches_clue(book, result_clue):
                matched_books.append(book)

    # 단서와 일치하는 작품이 부족하면 추가 작품에서 보충
    if len(matched_books) < 2:
        for book in books:
            if book["title"] not in [b["title"] for b in matched_books]:
                if matches_clue(book, result_clue):
                    matched_books.append(book)

            if len(matched_books) == 2:
                break

    if matched_books:
        for index, book in enumerate(matched_books[:2], start=1):
            st.markdown("### 📖 " + str(index) + ". " + book["title"])
            st.write("🗓️ 출판 연도: " + str(book["year"]) + "년")
            st.write("🌏 국가: " + book["country"])
            st.write("💡 작품 소개: " + book["description"])
            st.write("💖 추천 이유: " + book["reason"])

    else:
        st.warning(
            "선택한 단서에 맞는 책을 찾지 못했어. "
            "단서를 조금 더 넓게 입력해 줘!"
        )

    st.divider()

    # 영화 추천
    st.subheader("🎬 추천 영화 2편")

    movie_names = recommendations[result_mbti]["movies"]
    matched_movies = []

    for name in movie_names:
        for movie in movies:
            if movie["title"] == name and matches_clue(movie, result_clue):
                matched_movies.append(movie)

    # 단서와 일치하는 작품이 부족하면 추가 작품에서 보충
    if len(matched_movies) < 2:
        for movie in movies:
            if movie["title"] not in [m["title"] for m in matched_movies]:
                if matches_clue(movie, result_clue):
                    matched_movies.append(movie)

            if len(matched_movies) == 2:
                break

    if matched_movies:
        for index, movie in enumerate(matched_movies[:2], start=1):
            st.markdown("### 🍿 " + str(index) + ". " + movie["title"])
            st.write("🗓️ 개봉 연도: " + str(movie["year"]) + "년")
            st.write("🌏 국가: " + movie["country"])
            st.write("💡 작품 소개: " + movie["description"])
            st.write("💖 추천 이유: " + movie["reason"])

    else:
        st.warning(
            "선택한 단서에 맞는 영화를 찾지 못했어. "
            "다른 단서를 입력해 봐!"
        )

    st.divider()

    st.success(
        "🎉 추천 완료! 마음에 드는 작품을 골라서 즐겨 봐!"
    )

    st.caption(
        "📌 추천 결과는 등록된 작품 정보와 단서 규칙을 활용해 만들어져. "
        "모든 문장을 인공지능처럼 이해하는 것은 아니므로 "
        "단서는 간단하고 구체적으로 입력하는 것이 좋아."
    )

    st.caption(
        "📚 작품의 출판·개봉 연도와 소개는 참고용이야. "
        "실제 감상 전에는 도서관이나 공식 작품 정보를 확인해 줘."
    )
