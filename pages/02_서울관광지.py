
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 서울의 대표 관광지 10곳
places = [
    {
        "rank": 1,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796, "lon": 126.9770,
        "category": "역사·문화",
        "description": "조선 왕조의 대표 궁궐입니다. 근위병 교대식과 한복 체험으로 한국의 전통문화를 경험할 수 있습니다."
    },
    {
        "rank": 2,
        "name": "명동",
        "english": "Myeong-dong",
        "lat": 37.5636, "lon": 126.9850,
        "category": "쇼핑·먹거리",
        "description": "화장품 매장, 패션 상점, 길거리 음식으로 유명한 번화가입니다."
    },
    {
        "rank": 3,
        "name": "N서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512, "lon": 126.9882,
        "category": "전망·야경",
        "description": "남산에서 서울의 전경과 아름다운 야경을 감상할 수 있는 랜드마크입니다."
    },
    {
        "rank": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826, "lon": 126.9830,
        "category": "전통·산책",
        "description": "전통 한옥이 모여 있는 아름다운 동네입니다. 실제 주민이 거주하므로 조용히 둘러봐 주세요."
    },
    {
        "rank": 5,
        "name": "인사동",
        "english": "Insadong",
        "lat": 37.5710, "lon": 126.9850,
        "category": "공예·전통",
        "description": "전통 공예품, 갤러리, 찻집과 한국적인 기념품을 만나기 좋은 거리입니다."
    },
    {
        "rank": 6,
        "name": "홍대 거리",
        "english": "Hongdae",
        "lat": 37.5563, "lon": 126.9236,
        "category": "문화·엔터테인먼트",
        "description": "개성 있는 카페와 상점, 버스킹 공연과 젊은 예술 문화를 즐길 수 있습니다."
    },
    {
        "rank": 7,
        "name": "동대문디자인플라자(DDP)",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5670, "lon": 127.0095,
        "category": "건축·디자인",
        "description": "독특한 곡선형 건축물로 유명하며 전시와 디자인 행사, 야간 산책을 즐길 수 있습니다."
    },
    {
        "rank": 8,
        "name": "청계천",
        "english": "Cheonggyecheon Stream",
        "lat": 37.5692, "lon": 126.9788,
        "category": "도심·산책",
        "description": "서울 도심을 가로지르는 산책 공간입니다. 주변 명소를 둘러보며 쉬어 가기 좋습니다."
    },
    {
        "rank": 9,
        "name": "롯데월드",
        "english": "Lotte World",
        "lat": 37.5111, "lon": 127.0982,
        "category": "테마파크",
        "description": "실내외 놀이시설과 퍼레이드를 즐길 수 있는 대형 테마파크입니다."
    },
    {
        "rank": 10,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700, "lon": 126.9997,
        "category": "전통시장·음식",
        "description": "빈대떡과 김밥 등 다양한 한국 음식을 맛보고 전통시장 분위기를 경험할 수 있습니다."
    }
]

df = pd.DataFrame(places)

# 제목
st.title("🗺️ 서울 인기 관광지 TOP 10")
st.write(
    "서울 여행을 계획하는 외국인 방문객을 위한 "
    "관광지 지도와 간단한 소개입니다."
)

st.info(
    "이 목록은 공식 실시간 인기 순위가 아닌 "
    "서울의 대표 관광 명소를 소개하기 위한 참고용 목록입니다."
)

# 왼쪽 메뉴
with st.sidebar:
    st.header("🔎 지도 설정")

    categories = ["전체"] + sorted(df["category"].unique().tolist())

    selected_category = st.selectbox(
        "관광 유형 선택",
        categories
    )

    show_labels = st.checkbox(
        "지도에 관광지 이름 표시",
        value=True
    )

    st.markdown("---")
    st.write("지도에서 관광지 위치를 확인하고 아래에서 설명을 읽어보세요.")

# 선택한 관광 유형에 따라 필터링
if selected_category == "전체":
    filtered = df.copy()
else:
    filtered = df[df["category"] == selected_category].copy()

# 지도 중심 설정
view_state = pdk.ViewState(
    latitude=37.5665,
    longitude=126.9850,
    zoom=11,
    pitch=0
)

# 관광지 마커
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

# 지도에 관광지 이름 표시
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
            get_pixel_offset=[0, -12],
            pickable=False
        )
    )

# 지도 생성
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

# 지도 출력
st.subheader("📍 서울 관광지 지도")
st.pydeck_chart(deck, use_container_width=True)

# 관광지 설명
st.subheader("🏯 관광지 소개")
st.write(f"현재 표시된 관광지: **{len(filtered)}곳**")

# 두 개씩 나란히 표시
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

                google_maps_url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={place['lat']},{place['lon']}"
                )

                st.markdown(
                    f"[📍 Google 지도에서 위치 보기]({google_maps_url})"
                )

st.markdown("---")

st.caption(
    "관광지 좌표는 지도 표시를 위한 대표 위치입니다. "
    "방문 전 운영 시간과 휴무일을 확인하세요."
)
