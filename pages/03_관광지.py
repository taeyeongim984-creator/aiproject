
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(
    page_title="한국 여행 플래너",
    page_icon="🧳",
    layout="wide"
)

# -----------------------------
# 1. 도시별 관광지 데이터
# -----------------------------
cities = {
    "서울": {
        "center": [37.5665, 126.9850],
        "places": [
            {
                "name": "경복궁",
                "lat": 37.5796, "lon": 126.9770,
                "description": "조선 왕조의 대표 궁궐로 한국의 전통문화를 경험할 수 있어요."
            },
            {
                "name": "북촌한옥마을",
                "lat": 37.5826, "lon": 126.9830,
                "description": "전통 한옥과 아름다운 골목길을 볼 수 있어요."
            },
            {
                "name": "인사동",
                "lat": 37.5710, "lon": 126.9850,
                "description": "전통 공예품과 기념품, 한국식 찻집을 즐길 수 있어요."
            },
            {
                "name": "명동",
                "lat": 37.5636, "lon": 126.9850,
                "description": "쇼핑과 화장품, 다양한 길거리 음식으로 유명해요."
            },
            {
                "name": "N서울타워",
                "lat": 37.5512, "lon": 126.9882,
                "description": "서울의 전경과 야경을 감상하기 좋은 명소예요."
            },
            {
                "name": "홍대 거리",
                "lat": 37.5563, "lon": 126.9236,
                "description": "개성 있는 카페와 상점, 버스킹을 즐길 수 있어요."
            },
            {
                "name": "동대문디자인플라자",
                "lat": 37.5670, "lon": 127.0095,
                "description": "독특한 건축물과 디자인 전시가 유명해요."
            },
            {
                "name": "청계천",
                "lat": 37.5692, "lon": 126.9788,
                "description": "도심에서 산책하며 휴식을 취하기 좋아요."
            },
            {
                "name": "롯데월드",
                "lat": 37.5111, "lon": 127.0982,
                "description": "다양한 놀이기구와 퍼레이드를 즐길 수 있어요."
            },
            {
                "name": "광장시장",
                "lat": 37.5700, "lon": 126.9997,
                "description": "빈대떡과 김밥 등 한국 음식을 맛볼 수 있어요."
            }
        ],
        "schedule": [
            [
                ("09:30", "경복궁", "궁궐을 둘러보고 한국 전통문화를 체험해요."),
                ("11:30", "북촌한옥마을", "한옥 골목을 걸으며 사진을 찍어요."),
                ("13:00", "인사동", "점심 식사와 전통 기념품 쇼핑을 즐겨요."),
                ("15:00", "청계천", "도심 산책을 하며 잠시 쉬어 가요."),
                ("17:00", "명동", "쇼핑과 길거리 음식을 즐겨요."),
                ("19:00", "숙소 체크인", "명동이나 종로 주변 숙소에서 1박 해요.")
            ],
            [
                ("09:30", "광장시장", "시장 음식을 맛보며 아침을 시작해요."),
                ("11:00", "동대문디자인플라자", "건축물을 구경하고 전시를 둘러봐요."),
                ("14:00", "홍대 거리", "카페와 상점, 거리 문화를 즐겨요."),
                ("17:00", "N서울타워", "서울의 풍경을 감상하며 여행을 마무리해요.")
            ]
        ]
    },

    "부산": {
        "center": [35.1796, 129.0756],
        "places": [
            {
                "name": "해운대해수욕장",
                "lat": 35.1587, "lon": 129.1604,
                "description": "부산을 대표하는 해변으로 바다 풍경을 즐길 수 있어요."
            },
            {
                "name": "광안리해수욕장",
                "lat": 35.1532, "lon": 129.1187,
                "description": "광안대교 전망과 해변 카페로 유명해요."
            },
            {
                "name": "감천문화마을",
                "lat": 35.0975, "lon": 129.0106,
                "description": "알록달록한 집과 예술 작품이 있는 언덕 마을이에요."
            },
            {
                "name": "자갈치시장",
                "lat": 35.0968, "lon": 129.0305,
                "description": "부산의 해산물과 활기찬 전통시장 분위기를 경험할 수 있어요."
            },
            {
                "name": "BIFF 광장",
                "lat": 35.0987, "lon": 129.0278,
                "description": "영화 거리와 다양한 길거리 음식이 유명해요."
            },
            {
                "name": "해동용궁사",
                "lat": 35.1884, "lon": 129.2231,
                "description": "바다 옆에 자리한 아름다운 사찰이에요."
            }
        ],
        "schedule": [
            [
                ("09:30", "감천문화마을", "골목과 예술 작품을 구경해요."),
                ("12:00", "자갈치시장", "신선한 해산물과 부산 음식을 맛봐요."),
                ("13:30", "BIFF 광장", "영화 거리와 길거리 음식을 즐겨요."),
                ("16:00", "해운대해수욕장", "해변을 산책하고 바다를 감상해요."),
                ("18:30", "숙소 체크인", "해운대 주변 숙소에서 1박 해요.")
            ],
            [
                ("09:30", "해동용궁사", "바다 풍경과 사찰을 둘러봐요."),
                ("12:30", "해운대 주변", "점심을 먹고 주변을 구경해요."),
                ("15:00", "광안리해수욕장", "바다와 광안대교를 감상하며 여행을 마무리해요.")
            ]
        ]
    },

    "제주": {
        "center": [33.4996, 126.5312],
        "places": [
            {
                "name": "동문시장",
                "lat": 33.5113, "lon": 126.5262,
                "description": "제주 먹거리와 특산품을 구경하기 좋은 전통시장이에요."
            },
            {
                "name": "용두암",
                "lat": 33.5161, "lon": 126.5119,
                "description": "용의 머리를 닮은 바위와 바다 풍경을 볼 수 있어요."
            },
            {
                "name": "성산일출봉",
                "lat": 33.4584, "lon": 126.9425,
                "description": "제주의 대표적인 자연 명소로 멋진 해안 풍경을 감상할 수 있어요."
            },
            {
                "name": "섭지코지",
                "lat": 33.4241, "lon": 126.9270,
                "description": "해안 산책로와 독특한 바위 풍경이 아름다운 곳이에요."
            },
            {
                "name": "협재해수욕장",
                "lat": 33.3940, "lon": 126.2396,
                "description": "맑은 바다와 아름다운 해변으로 유명해요."
            },
            {
                "name": "한라산국립공원",
                "lat": 33.3617, "lon": 126.5292,
                "description": "제주의 자연과 산악 풍경을 만날 수 있는 국립공원이에요."
            }
        ],
        "schedule": [
            [
                ("09:30", "용두암", "제주 바다와 기암 풍경을 감상해요."),
                ("11:00", "동문시장", "제주 특산물과 점심을 즐겨요."),
                ("13:30", "협재해수욕장", "아름다운 바다를 감상하며 산책해요."),
                ("17:00", "숙소 체크인", "제주시 또는 숙소 예약 지역에서 1박 해요.")
            ],
            [
                ("09:00", "성산일출봉", "제주의 대표 자연 명소를 둘러봐요."),
                ("11:30", "섭지코지", "해안 산책로와 바다 풍경을 감상해요."),
                ("15:00", "한라산국립공원", "체력과 날씨에 맞춰 탐방로를 즐겨요.")
            ]
        ]
    }
}

# -----------------------------
# 2. 도시 선택
# -----------------------------
st.title("🧳 한국 여행 플래너")
st.write("가고 싶은 도시를 선택하면 관광지도와 1박 2일 일정이 나옵니다.")

city_name = st.selectbox(
    "✈️ 여행하고 싶은 도시를 선택하세요",
    list(cities.keys())
)

city = cities[city_name]
places_df = pd.DataFrame(city["places"])

st.header(f"📍 {city_name} 관광지도")

st.caption(
    "지도에서 관광지 위치를 확인하세요. "
    "마커 위에 마우스를 올리면 장소 이름과 설명이 표시됩니다."
)

# -----------------------------
# 3. 지도 설정
# -----------------------------
view_state = pdk.ViewState(
    latitude=city["center"][0],
    longitude=city["center"][1],
    zoom=10 if city_name != "제주" else 9,
    pitch=0
)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=places_df,
    get_position="[lon, lat]",
    get_radius=150,
    radius_min_pixels=6,
    radius_max_pixels=16,
    get_fill_color=[220, 55, 55, 220],
    get_line_color=[255, 255, 255, 255],
    line_width_min_pixels=1,
    pickable=True
)

text_layer = pdk.Layer(
    "TextLayer",
    data=places_df,
    get_position="[lon, lat]",
    get_text="name",
    get_size=12,
    get_color=[30, 30, 30, 255],
    get_alignment_baseline="'bottom'",
    get_pixel_offset=[0, -12]
)

deck = pdk.Deck(
    layers=[scatter_layer, text_layer],
    initial_view_state=view_state,
    map_style=(
        "https://basemaps.cartocdn.com/"
        "gl/positron-gl-style/style.json"
    ),
    tooltip={
        "text": "{name}\n{description}"
    }
)

st.pydeck_chart(deck, use_container_width=True)

# -----------------------------
# 4. 관광지 설명
# -----------------------------
st.header(f"🏞️ {city_name} 주요 관광지")

for start in range(0, len(places_df), 2):
    cols = st.columns(2)

    for col, (_, place) in zip(
        cols,
        places_df.iloc[start:start + 2].iterrows()
    ):
        with col:
            with st.container(border=True):
                st.subheader(place["name"])
                st.write(place["description"])

                url = (
                    "https://www.google.com/maps/search/?api=1"
                    f"&query={place['lat']},{place['lon']}"
                )

                st.markdown(
                    f"[📍 지도에서 위치 보기]({url})"
                )

# -----------------------------
# 5. 1박 2일 일정
# -----------------------------
st.header(f"🗓️ {city_name} 1박 2일 추천 일정")

st.info(
    "추천 일정은 참고용입니다. 실제 이동 시간과 운영 시간, "
    "날씨에 따라 일정을 조정하세요."
)

day_tabs = st.tabs(["📅 1일 차", "📅 2일 차"])

for day_index, tab in enumerate(day_tabs):
    with tab:
        if day_index == 0:
            st.subheader("1일 차 · 관광과 숙소 체크인")
        else:
            st.subheader("2일 차 · 여행과 마무리")

        for time, name, description in city["schedule"][day_index]:
            with st.container(border=True):
                col1, col2 = st.columns([1, 4])

                with col1:
                    st.markdown(f"### {time}")

                with col2:
                    st.markdown(f"**{name}**")
                    st.write(description)

                    place_match = places_df[
                        places_df["name"] == name
                    ]

                    if not place_match.empty:
                        place = place_match.iloc[0]

                        url = (
                            "https://www.google.com/maps/search/?api=1"
                            f"&query={place['lat']},{place['lon']}"
                        )

                        st.markdown(
                            f"[📍 위치 확인]({url})"
                        )

st.markdown("---")
st.caption(
    "한국 여행 플래너 | 관광지와 일정은 참고용 추천이며 "
    "교통편 및 숙소 예약은 별도로 확인해야 합니다."
)
