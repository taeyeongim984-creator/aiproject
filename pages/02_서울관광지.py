
import streamlit as st
import pandas as pd
import pydeck as pdk

# ---------------------------------
# 1. 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="서울 관광지도 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# ---------------------------------
# 2. 서울 관광지 데이터
# ---------------------------------
places = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐입니다. 한복 체험과 전통문화를 즐길 수 있습니다."
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636,
        "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "화장품, 패션 상점과 다양한 길거리 음식으로 유명합니다."
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산에서 서울의 아름다운 전경과 야경을 감상할 수 있습니다."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·산책",
        "description": "전통 한옥이 모여 있는 마을입니다. 주민을 배려해 조용히 관람해 주세요."
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5710,
        "lon": 126.9850,
        "category": "공예·전통",
        "description": "전통 공예품, 갤러리, 찻집과 한국적인 기념품을 만나기 좋습니다."
    },
    {
        "rank": 6,
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "개성 있는 카페와 상점, 거리 공연과 젊은 문화를 즐길 수 있습니다."
    },
    {
        "rank": 7,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5670,
        "lon": 127.0095,
        "category": "건축·디자인",
        "description": "독특한 건축물과 전시, 디자인 행사로 유명한 장소입니다."
    },
    {
        "rank": 8,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5692,
        "lon": 126.9788,
        "category": "도심·산책",
        "description": "서울 도심에서 물길을 따라 산책하고 휴식할 수 있습니다."
    },
    {
        "rank": 9,
        "name": "롯데월드",
        "english": "Lotte World",
        "lat": 37.5111,
        "lon": 127.0982,
        "category": "테마파크",
        "description": "실내외 놀이시설과 퍼레이드를 즐길 수 있는 대형 테마파크입니다."
    },
    {
        "rank": 10,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡과 김밥 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다."
    }
]

df = pd.DataFrame(places)

# ---------------------------------
# 3. 서울 1박 2일 추천 일정
# ---------------------------------
day1 = [
    ("09:00", "경복궁", "궁궐 관람과 한국 전통문화 체험"),
    ("11:00", "북촌한옥마을", "한옥 골목 산책과 사진 촬영"),
    ("12:30", "인사동", "점심 식사와 전통 거리 구경"),
    ("14:30", "청계천", "도심 산책과 휴식"),
    ("16:30", "명동", "쇼핑과 길거리 음식"),
    ("19:00", "N서울타워", "서울의 아름다운 야경 감상")
]

day2 = [
    ("09:30", "광장시장", "전통시장 음식 맛보기"),
    ("11:00", "동대문디자인플라자", "독특한 건축물과 전시 관람"),
    ("13:00", "홍대 거리", "점심 식사와 거리 구경"),
    ("15:00", "홍대 카페", "카페에서 휴식"),
    ("16:30", "여행 마무리", "기념품 쇼핑 후 이동")
]

# ---------------------------------
# 4. 제목과 안내
# ---------------------------------
st.title("🗺️ 서울 인기 관광지 TOP 10")
st.write(
    "서울을 방문하는 외국인 여행객을 위한 "
    "관광지 지도와 1박 2일 추천 여행 일정입니다."
)

st.info(
    "관광지는 서울의 대표 명소를 소개하기 위한 참고용 목록이며, "
    "공식 실시간 인기 순위는 아닙니다."
)

# ---------------------------------
# 5. 사이드바 설정
# ---------------------------------
with st.sidebar:
    st.header("🔎 지도 설정")

    categories = ["전체"] + sorted(
        df["category"].unique().tolist()
    )

    selected_category = st.selectbox(
        "관광 유형 선택",
        categories
    )

    show_labels = st.checkbox(
        "지도에 관광지 이름 표시",
        value=True
    )

    st.markdown("---")
    st.write("관광지를 선택해 종류별로 확인할 수 있습니다.")

# 관광 유형 필터
if selected_category == "전체":
    filtered = df.copy()
else:
    filtered = df[
        df["category"] == selected_category
    ].copy()

# ---------------------------------
# 6. 서울 지도 만들기
# ---------------------------------
st.subheader("📍 서울 관광지 지도")

view_state = pdk.ViewState(
    latitude=37.5665,
    longitude=126.9850,
    zoom=11,
    pitch=0
)

layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position="[lon, lat]",
        get_radius=100,
        radius_min_pixels=6,
        radius_max_pixels=18,
        get_fill_color=[220, 55, 55, 220],
        get_line_color=[255, 255, 255, 255],
        line_width_min_pixels=1,
        pickable=True
    )
]

# 지도 위에 이름 표시
if show_labels:
    layers.append(
        pdk.Layer(
            "TextLayer",
            data=filtered,
            get_position="[lon, lat]",
            get_text="name",
            get_size=13,
            get_color=[30, 30, 30, 255],
            get_alignment_baseline="'bottom'",
            get_pixel_offset=[0, -12]
        )
    )

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style=(
        "https://basemaps.cartocdn.com/"
        "gl/positron-gl-style/style.json"
    ),
    tooltip={
        "text": "{rank}. {name}\n{english}\n{category}"
    }
)

st.pydeck_chart(deck, use_container_width=True)

# ---------------------------------
# 7. 관광지 설명
# ---------------------------------
st.subheader("🏯 서울 관광지 소개")
st.write(f"현재 표시된 관광지: **{len(filtered)}곳**")

for start in range(0, len(filtered), 2):
    cols = st.columns(2)
    rows = filtered.iloc[start:start + 2]

    for col, (_, place) in zip(cols, rows.iterrows()):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"### {place['rank']}. {place['name']}"
                )

                st.caption(
                    f"{place['english']} · {place['category']}"
                )

                st.write(place["description"])

                maps_url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={place['lat']},{place['lon']}"
                )

                st.markdown(
                    f"[📌 Google 지도에서 위치 보기]({maps_url})"
                )

# ---------------------------------
# 8. 지도와 관광지 아래 1박 2일 일정
# ---------------------------------
st.markdown("---")
st.header("🗓️ 서울 1박 2일 추천 여행 일정")

st.write(
    "서울의 주요 관광지를 효율적으로 둘러볼 수 있도록 "
    "구성한 예시 일정입니다."
)

st.caption(
    "방문 순서와 시간은 추천 예시입니다. "
    "교통 상황, 입장 시간과 휴무일에 따라 조정해 주세요."
)

tab1, tab2 = st.tabs([
    "☀️ 첫째 날 (DAY 1)",
    "🌙 둘째 날 (DAY 2)"
])

# 첫째 날
with tab1:
    st.subheader("DAY 1 | 역사와 서울의 야경")

    for time, place, activity in day1:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])

            with col1:
                st.markdown(f"**{time}**")

            with col2:
                st.markdown(f"📍 **{place}**")
                st.write(activity)

# 둘째 날
with tab2:
    st.subheader("DAY 2 | 시장 음식과 젊은 문화")

    for time, place, activity in day2:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])

            with col1:
                st.markdown(f"**{time}**")

            with col2:
                st.markdown(f"📍 **{place}**")
                st.write(activity)

# ---------------------------------
# 9. 여행 팁
# ---------------------------------
st.markdown("---")
st.subheader("💡 서울 여행 팁")

st.markdown("""
- **교통:** 지하철과 버스를 활용하면 편리합니다.
- **준비물:** 편한 신발과 교통카드를 준비하세요.
- **궁궐 방문:** 경복궁의 운영 시간과 휴무일을 미리 확인하세요.
- **북촌 방문:** 실제 주민이 거주하므로 정숙하게 관람하세요.
- **일정 조정:** 관광지 사이 이동 시간과 대기 시간을 고려하세요.
""")

st.caption(
    "지도 배경을 표시하려면 인터넷 연결이 필요합니다. "
    "관광지 좌표는 지도에 표시하기 위한 대표 위치입니다."
)
