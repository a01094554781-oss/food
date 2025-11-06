import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------------
# 페이지 기본 설정
# ----------------------------------
st.set_page_config(page_title="서울 음식점 혼잡도 지도", layout="wide")
st.title("🍜 서울 음식점 혼잡도 지도 (3000개 시뮬레이션)")
st.markdown("시간대별로 서울 전역의 음식점 혼잡도를 시각화했습니다. \
지도는 확대/이동/회전 모두 가능합니다 🗺️")

# ----------------------------------
# 데이터 생성
# ----------------------------------
@st.cache_data
def generate_data(n=3000):
    np.random.seed(42)
    
    # 서울 근처 위도/경도 범위
    latitudes = np.random.uniform(37.45, 37.70, n)
    longitudes = np.random.uniform(126.80, 127.10, n)
    
    # 랜덤한 음식 카테고리
    categories = np.random.choice(
        ["한식", "중식", "일식", "양식", "분식", "패스트푸드", "카페", "아시아음식", "멕시코음식", "건강식"],
        n
    )
    
    # 랜덤 음식점 이름
    name_prefix = ["맛집", "고향", "명가", "리미티드", "스페셜", "정통", "하우스", "오리지널", "서울", "트렌디"]
    name_suffix = ["한식당", "식당", "다이닝", "레스토랑", "카페", "그릴", "키친", "라운지", "하우스", "포차"]
    names = [f"{np.random.choice(name_prefix)} {np.random.choice(name_suffix)}" for _ in range(n)]
    
    # 가격대, 평점, 시간대별 혼잡도
    price_range = np.random.choice(["₩", "₩₩", "₩₩₩"], n, p=[0.4, 0.4, 0.2])
    ratings = np.round(np.random.normal(4.2, 0.4, n), 1)
    ratings = np.clip(ratings, 2.5, 5.0)
    
    # 시간대 (아침/점심/저녁)
    hours = ["아침", "점심", "저녁"]
    congestion = {h: np.random.randint(10, 100, n) for h in hours}
    
    df = pd.DataFrame({
        "name": names,
        "category": categories,
        "price_range": price_range,
        "rating": ratings,
        "lat": latitudes,
        "lon": longitudes,
        "morning": congestion["아침"],
        "lunch": congestion["점심"],
        "dinner": congestion["저녁"]
    })
    return df

data = generate_data(3000)

# ----------------------------------
# 사이드바 필터
# ----------------------------------
st.sidebar.header("🔍 필터 옵션")
selected_category = st.sidebar.multiselect("음식 종류", sorted(data["category"].unique()), default=data["category"].unique())
selected_price = st.sidebar.multiselect("가격대", ["₩", "₩₩", "₩₩₩"], default=["₩", "₩₩", "₩₩₩"])
selected_hour = st.sidebar.radio("시간대 선택", ["아침", "점심", "저녁"])
map_style = st.sidebar.selectbox("지도 스타일", ["open-street-map", "carto-positron", "stamen-toner", "carto-darkmatter"])
min_rating = st.sidebar.slider("최소 평점", 2.5, 5.0, 3.5, 0.1)

# ----------------------------------
# 필터 적용
# ----------------------------------
filtered = data[
    (data["category"].isin(selected_category)) &
    (data["price_range"].isin(selected_price)) &
    (data["rating"] >= min_rating)
].copy()

# ----------------------------------
# 지도 시각화
# ----------------------------------
st.subheader("🗺️ 음식점 위치 지도")

fig = px.scatter_mapbox(
    filtered,
    lat="lat",
    lon="lon",
    color="rating",
    size=filtered[selected_hour.lower()],
    hover_name="name",
    hover_data=["category", "rating", "price_range"],
    color_continuous_scale="RdYlGn",
    size_max=20,
    zoom=11,
    height=650,
)
fig.update_layout(mapbox_style=map_style, mapbox_zoom=11, mapbox_center={"lat": 37.56, "lon": 126.98})
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# 데이터 요약
# ----------------------------------
st.subheader("📊 데이터 요약")
col1, col2, col3 = st.columns(3)
col1.metric("총 음식점 수", f"{len(filtered):,} 개")
col2.metric("평균 평점", f"{filtered['rating'].mean():.2f} ⭐")
col3.metric(f"{selected_hour} 평균 혼잡도", f"{filtered[selected_hour.lower()].mean():.1f} %")

# ----------------------------------
# 표 보기
# ----------------------------------
with st.expander("🔽 음식점 세부 목록 보기"):
    st.dataframe(filtered[["name", "category", "price_range", "rating", "lat", "lon", "morning", "lunch", "dinner"]])
