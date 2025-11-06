import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(page_title="서울 음식점 대시보드", layout="wide")
st.title("🍜 서울 음식점 탐색 대시보드")
st.markdown("서울 전역의 음식점 3000개 데이터를 바탕으로, \
현재 위치 주변의 식당을 탐색하고 직접 추가할 수 있습니다!")

# -----------------------------
# 음식점 데이터 생성 함수
# -----------------------------
@st.cache_data
def generate_data(n=3000):
    np.random.seed(42)
    
    latitudes = np.random.uniform(37.45, 37.70, n)
    longitudes = np.random.uniform(126.80, 127.10, n)
    
    categories = np.random.choice(
        ["한식", "중식", "일식", "양식", "분식", "패스트푸드", "카페", "아시아음식", "멕시코음식", "건강식"],
        n
    )
    
    name_prefix = ["맛집", "고향", "명가", "리미티드", "스페셜", "정통", "하우스", "오리지널", "서울", "트렌디"]
    name_suffix = ["한식당", "식당", "다이닝", "레스토랑", "카페", "그릴", "키친", "라운지", "하우스", "포차"]
    names = [f"{np.random.choice(name_prefix)} {np.random.choice(name_suffix)}" for _ in range(n)]
    
    price_range = np.random.choice(["₩", "₩₩", "₩₩₩"], n, p=[0.4, 0.4, 0.2])
    ratings = np.round(np.random.normal(4.2, 0.4, n), 1)
    ratings = np.clip(ratings, 2.5, 5.0)
    
    df = pd.DataFrame({
        "이름": names,
        "카테고리": categories,
        "가격대": price_range,
        "위도": latitudes,
        "경도": longitudes,
        "평점": ratings,
    })
    return df

# -----------------------------
# 초기 데이터 불러오기
# -----------------------------
if "restaurants" not in st.session_state:
    st.session_state["restaurants"] = generate_data(3000)
df = st.session_state["restaurants"]

# -----------------------------
# 사이드바 설정
# -----------------------------
st.sidebar.header("🔍 탐색 옵션")

category = st.sidebar.selectbox("🍱 카테고리 선택", ["전체"] + sorted(df["카테고리"].unique().tolist()))
rating_min = st.sidebar.slider("⭐ 최소 평점", 2.5, 5.0, 4.0, 0.1)
map_style = st.sidebar.selectbox("🗺️ 지도 스타일", [
    "open-street-map", "carto-positron", "stamen-terrain", "stamen-toner", "carto-darkmatter"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📍 현재 위치 설정 (서울 기준)")
lat_user = st.sidebar.slider("위도 (37.45~37.70)", 37.45, 37.70, 37.56, 0.001)
lon_user = st.sidebar.slider("경도 (126.80~127.10)", 126.80, 127.10, 126.98, 0.001)
radius = st.sidebar.slider("📏 반경 (km)", 1, 10, 3)

# -----------------------------
# 거리 계산 (Haversine)
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    return 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

df["거리(km)"] = df.apply(lambda row: haversine(lat_user, lon_user, row["위도"], row["경도"]), axis=1)

# -----------------------------
# 필터 적용
# -----------------------------
filtered = df[df["평점"] >= rating_min]
if category != "전체":
    filtered = filtered[filtered["카테고리"] == category]
filtered = filtered[filtered["거리(km)"] <= radius]

# -----------------------------
# 지도 시각화
# -----------------------------
st.subheader("🗺️ 음식점 지도 보기")

if filtered.empty:
    st.warning("조건에 맞는 음식점이 없습니다 😥")
else:
    fig = px.scatter_mapbox(
        filtered,
        lat="위도",
        lon="경도",
        color="평점",
        size="평점",
        color_continuous_scale="RdYlGn",
        size_max=20,
        zoom=12,
        hover_name="이름",
        hover_data=["카테고리", "가격대", "평점", "거리(km)"],
        height=650
    )

    # 현재 위치 마커
    fig.add_scattermapbox(
        lat=[lat_user],
        lon=[lon_user],
        mode="markers+text",
        marker=dict(size=15, color="blue"),
        text=["📍 현재 위치"],
        textposition="top right"
    )

    fig.update_layout(
        mapbox_style=map_style,
        mapbox_center={"lat": lat_user, "lon": lon_user},
        margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 음식점 추가 기능
# -----------------------------
st.markdown("---")
st.subheader("➕ 새 음식점 추가하기")

with st.form("add_restaurant_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("음식점 이름")
        category_new = st.text_input("카테고리 (예: 한식, 양식 등)")
        rating = st.slider("평점", 0.0, 5.0, 4.5, 0.1)
    with col2:
        lat = st.number_input("위도", min_value=37.45, max_value=37.70, value=lat_user, step=0.0001)
        lon = st.number_input("경도", min_value=126.80, max_value=127.10, value=lon_user, step=0.0001)
        price = st.selectbox("가격대", ["₩", "₩₩", "₩₩₩"])
    submitted = st.form_submit_button("추가하기")

    if submitted:
        new_row = pd.DataFrame([{
            "이름": name, "카테고리": category_new, "가격대": price,
            "위도": lat, "경도": lon, "평점": rating,
        }])
        st.session_state["restaurants"] = pd.concat([df, new_row], ignore_index=True)
        st.success(f"✅ '{name}' 음식점이 추가되었습니다! (지도 새로고침 시 반영)")

# -----------------------------
# 카테고리별 평균 평점
# -----------------------------
st.markdown("---")
st.subheader("📊 카테고리별 평균 평점")
avg_ratings = df.groupby("카테고리")["평점"].mean().reset_index()
st.bar_chart(avg_ratings.set_index("카테고리"))
