import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# 기본 페이지 설정
# -----------------------------
st.set_page_config(page_title="서울 음식점 지도", layout="wide")
st.title("🍴 서울 음식점 혼잡도 지도")
st.markdown("시간대별로 서울의 음식점 혼잡도를 확인해보세요!")

# -----------------------------
# 초기 데이터
# -----------------------------
if "restaurants" not in st.session_state:
    st.session_state["restaurants"] = pd.DataFrame({
        "이름": ["한남돈까스", "을지로냉면", "홍대버거", "강남스시", "성수카페", "망원분식", "종로우동", "잠실피자", "건대치킨", "이태원파스타"],
        "카테고리": ["양식", "한식", "양식", "일식", "카페", "분식", "한식", "양식", "치킨", "양식"],
        "위도": [37.538, 37.565, 37.556, 37.501, 37.544, 37.556, 37.572, 37.514, 37.541, 37.534],
        "경도": [127.002, 127.004, 126.922, 127.027, 127.056, 126.905, 126.978, 127.099, 127.072, 126.995],
        "평점": [4.7, 4.2, 3.8, 4.9, 4.5, 4.1, 3.9, 4.6, 4.3, 4.8],
        "주소": [
            "서울 용산구 한남동", "서울 중구 을지로", "서울 마포구 홍대입구", "서울 강남구 역삼동",
            "서울 성동구 성수동", "서울 마포구 망원동", "서울 종로구 종로3가", "서울 송파구 잠실동",
            "서울 광진구 화양동", "서울 용산구 이태원동"
        ]
    })

df = st.session_state["restaurants"]

# -----------------------------
# 사이드바 옵션
# -----------------------------
st.sidebar.header("🔍 탐색 옵션")

category = st.sidebar.selectbox("🍱 카테고리 선택", ["전체"] + sorted(df["카테고리"].unique().tolist()))
rating_min = st.sidebar.slider("⭐ 최소 평점", 0.0, 5.0, 4.0, 0.1)
map_style = st.sidebar.selectbox("🗺️ 지도 스타일", [
    "open-street-map", "carto-positron", "stamen-terrain", "stamen-toner", "carto-darkmatter"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📍 현재 위치 설정")
lat_user = st.sidebar.slider("위도 (37.45~37.60)", 37.45, 37.60, 37.55, 0.001)
lon_user = st.sidebar.slider("경도 (126.90~127.10)", 126.90, 127.10, 127.00, 0.001)
radius = st.sidebar.slider("📏 반경 (km)", 1, 10, 3)

# -----------------------------
# 혼잡도 데이터 (시간대별)
# -----------------------------
time = st.slider("⏰ 시간 선택", 0, 23, 12, 1)

# 시간대별로 혼잡도 변화를 랜덤하게 시뮬레이션
np.random.seed(time)
df["혼잡도"] = (np.sin((time - np.linspace(8, 22, len(df))) / 3) + 1.5 + np.random.rand(len(df)) * 0.5) * 50
df["혼잡도"] = df["혼잡도"].clip(10, 100)  # 10~100 사이

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

df["거리(km)"] = df.apply(lambda r: haversine(lat_user, lon_user, r["위도"], r["경도"]), axis=1)

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
st.subheader(f"🗺️ {time}시 기준 서울 음식점 혼잡도 지도")

if filtered.empty:
    st.warning("조건에 맞는 음식점이 없습니다.")
else:
    fig = px.scatter_mapbox(
        filtered,
        lat="위도",
        lon="경도",
        color="혼잡도",
        size="혼잡도",
        color_continuous_scale="YlOrRd",
        size_max=25,
        zoom=12,
        hover_name="이름",
        hover_data=["주소", "카테고리", "평점", "혼잡도", "거리(km)"],
        height=650
    )

    # 현재 위치 표시
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
        margin={"r":0, "t":0, "l":0, "b":0},
        coloraxis_colorbar=dict(title="혼잡도(%)")
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 시간대별 혼잡도 평균 그래프
# -----------------------------
st.markdown("---")
st.subheader("📈 시간대별 평균 혼잡도 변화 (시뮬레이션)")

hours = np.arange(0, 24)
avg_congestion = [np.mean((np.sin((h - np.linspace(8, 22, len(df))) / 3) + 1.5) * 50) for h in hours]
chart_data = pd.DataFrame({"시간": hours, "평균혼잡도": avg_congestion})
st.line_chart(chart_data.set_index("시간"))
