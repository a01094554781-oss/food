import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import random, time

# --- 앱 기본 설정 ---
st.set_page_config(page_title="서울 음식점 혼잡도 실시간 지도", layout="wide")

st.title("🍽️ 서울 음식점 실시간 혼잡도 지도")
st.caption("10초마다 혼잡도가 갱신됩니다. (시뮬레이션)")

# --- 서울 내 임의 음식점 데이터 생성 ---
def generate_restaurant_data(n=80):
    np.random.seed(42)
    latitudes = np.random.uniform(37.48, 37.65, n)
    longitudes = np.random.uniform(126.85, 127.08, n)
    restaurants = []
    names = ["김밥천국", "홍콩반점", "맥도날드", "버거킹", "이디야커피", "투썸플레이스",
             "한솥도시락", "교촌치킨", "BBQ치킨", "피자스쿨", "스타벅스", "죠스떡볶이",
             "신전떡볶이", "명랑핫도그", "파리바게뜨", "던킨도너츠", "롯데리아", "노브랜드버거"]
    congestion_levels = ["낮음", "보통", "높음", "매우 높음"]

    for i in range(n):
        restaurants.append({
            "이름": random.choice(names),
            "평점": round(np.random.uniform(2.5, 5.0), 1),
            "혼잡도": random.choice(congestion_levels),
            "lat": latitudes[i],
            "lon": longitudes[i]
        })
    return pd.DataFrame(restaurants)

# --- 색상 매핑 ---
def apply_colors(df):
    color_map = {
        "낮음": [0, 200, 0],
        "보통": [255, 255, 0],
        "높음": [255, 165, 0],
        "매우 높음": [255, 0, 0]
    }
    df["color"] = df["혼잡도"].map(color_map)
    return df

# --- 현재 위치 입력 ---
st.sidebar.header("📍 내 위치 설정")
user_lat = st.sidebar.number_input("위도(lat)", value=37.55, format="%.6f")
user_lon = st.sidebar.number_input("경도(lon)", value=126.98, format="%.6f")

# --- 지도 스타일 선택 ---
st.sidebar.header("🗺️ 지도 스타일")
map_style = st.sidebar.selectbox(
    "지도 스타일 선택",
    ["mapbox://styles/mapbox/streets-v11", 
     "mapbox://styles/mapbox/light-v10", 
     "mapbox://styles/mapbox/dark-v10",
     "mapbox://styles/mapbox/outdoors-v11"]
)

# --- 반경 내 필터 ---
radius = st.sidebar.slider("근처 탐색 반경 (m)", 100, 3000, 1000)
def within_radius(row, center_lat, center_lon, r_m=1000):
    R = 6371000
    d_lat = np.radians(row["lat"] - center_lat)
    d_lon = np.radians(row["lon"] - center_lon)
    a = np.sin(d_lat/2)**2 + np.cos(np.radians(center_lat)) * np.cos(np.radians(row["lat"])) * np.sin(d_lon/2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a)) < r_m

# --- 실시간 시뮬레이션 ---
placeholder = st.empty()
data = generate_restaurant_data()

for i in range(100):  # 100번(약 1000초 = 16분) 갱신
    # 혼잡도 무작위 변동
    congestion_levels = ["낮음", "보통", "높음", "매우 높음"]
    data["혼잡도"] = data["혼잡도"].apply(lambda x: random.choice(congestion_levels))
    data = apply_colors(data)

    nearby = data[data.apply(lambda row: within_radius(row, user_lat, user_lon, radius), axis=1)]

    # 지도 갱신
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=nearby,
        get_position='[lon, lat]',
        get_fill_color='color',
        get_radius=120,
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=user_lat, longitude=user_lon, zoom=12)

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style=map_style,
        tooltip={"text": "🏠 {이름}\n⭐ 평점: {평점}\n📊 혼잡도: {혼잡도}"}
    )

    with placeholder.container():
        st.pydeck_chart(r)
        st.markdown(f"### 🔄 최근 업데이트: {time.strftime('%H:%M:%S')}")
        st.caption("10초마다 자동으로 갱신됩니다.")
        st.bar_chart(data["혼잡도"].value_counts())

    time.sleep(10)
