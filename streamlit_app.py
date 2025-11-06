import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -----------------------------
# 🌐 기본 설정
# -----------------------------
st.set_page_config(page_title="서울 음식점 탐색 지도", layout="wide")
st.title("🍴 서울 음식점 탐색 지도")
st.markdown("서울 전역의 음식점을 평점, 시간대별 혼잡도, 거리, 지도 스타일 등으로 탐색해보세요!")

# -----------------------------
# 📍 가상 데이터 생성 함수
# -----------------------------
def generate_data(n=3000):
    np.random.seed(42)
    latitudes = np.random.uniform(37.45, 37.70, n)
    longitudes = np.random.uniform(126.80, 127.10, n)
    categories = np.random.choice(
        ["한식", "중식", "일식", "양식", "분식", "패스트푸드", "카페", "아시아음식", "멕시코음식", "건강식", "치킨", "디저트"],
        n
    )
    name_prefix = ["맛집", "고향", "명가", "리미티드", "스페셜", "정통", "하우스", "오리지널", "서울", "트렌디", "핫플", "로컬"]
    name_suffix = ["한식당", "식당", "다이닝", "레스토랑", "카페", "그릴", "키친", "라운지", "하우스", "포차", "펍"]
    names = [f"{np.random.choice(name_prefix)} {np.random.choice(name_suffix)}" for _ in range(n)]
    ratings = np.round(np.random.uniform(2.0, 5.0, n), 1)
    
    # 각 시간대별 혼잡도 (0~1 사이 비율)
    morning = np.round(np.random.uniform(0.2, 0.8, n), 2)
    lunch = np.round(np.random.uniform(0.3, 1.0, n), 2)
    evening = np.round(np.random.uniform(0.4, 1.0, n), 2)
    
    return pd.DataFrame({
        "이름": names,
        "카테고리": categories,
        "위도": latitudes,
        "경도": longitudes,
        "평점": ratings,
        "혼잡도(오전)": morning,
        "혼잡도(점심)": lunch,
        "혼잡도(저녁)": evening
    })

# -----------------------------
# 🧭 초기 데이터 (세션 유지)
# -----------------------------
if "restaurants" not in st.session_state:
    st.session_state["restaurants"] = generate_data(3000)
df = st.session_state["restaurants"]

# -----------------------------
# ⚙️ 사이드바 옵션
# -----------------------------
st.sidebar.header("🔍 탐색 옵션")

category = st.sidebar.selectbox("🍱 카테고리 선택", ["전체"] + sorted(df["카테고리"].unique().tolist()))
rating_min = st.sidebar.slider("⭐ 최소 평점", 0.0, 5.0, 3.0, 0.1)
map_style = st.sidebar.selectbox("🗺️ 지도 스타일", [
    "open-street-map", "carto-positron", "stamen-terrain", "stamen-toner", "carto-darkmatter"
])

st.sidebar.markdown("---")
st.sidebar.subheader("🕒 시간대 선택")
time_slot = st.sidebar.radio("현재 시간대", ["오전", "점심", "저녁"], horizontal=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 현재 위치 설정 (서울 기준)")
lat_user = st.sidebar.slider("위도 (37.45~37.70)", 37.45, 37.70, 37.55, 0.001)
lon_user = st.sidebar.slider("경도 (126.80~127.10)", 126.80, 127.10, 127.00, 0.001)
radius = st.sidebar.slider("📏 반경 (km)", 1, 10, 4)

# -----------------------------
# 📐 거리 계산 (Haversine)
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
# 🔎 필터 적용
# -----------------------------
filtered = df[df["평점"] >= rating_min]
if category != "전체":
    filtered = filtered[filtered["카테고리"] == category]
filtered = filtered[filtered["거리(km)"] <= radius]

# -----------------------------
# ⏰ 혼잡도 컬럼 선택
# -----------------------------
congestion_col = f"혼잡도({time_slot})"
filtered = filtered.copy()
filtered["혼잡도"] = filtered[congestion_col]

# -----------------------------
# 🗺️ 지도 시각화
# -----------------------------
st.subheader(f"🗺️ 음식점 지도 보기 ({time_slot} 기준 혼잡도)")

if filtered.empty:
    st.warning("조건에 맞는 음식점이 없습니다.")
else:
    fig = px.scatter_mapbox(
        filtered,
        lat="위도",
        lon="경도",
        color="평점",
        size="혼잡도",
        color_continuous_scale="RdYlGn",
        size_max=25,
        zoom=11,
        hover_name="이름",
        hover_data=["카테고리", "평점", "혼잡도", "거리(km)"],
        height=700
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
        dragmode="zoom"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ➕ 음식점 추가 기능
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
        lat = st.number_input("위도", min_value=37.45, max_value=37.70, value=37.55, step=0.0001)
        lon = st.number_input("경도", min_value=126.80, max_value=127.10, value=127.00, step=0.0001)
        congestion_m = st.slider("오전 혼잡도", 0.0, 1.0, 0.5, 0.1)
        congestion_l = st.slider("점심 혼잡도", 0.0, 1.0, 0.7, 0.1)
        congestion_e = st.slider("저녁 혼잡도", 0.0, 1.0, 0.8, 0.1)
    submitted = st.form_submit_button("추가하기")

    if submitted:
        new_row = pd.DataFrame([{
            "이름": name,
            "카테고리": category_new,
            "위도": lat,
            "경도": lon,
            "평점": rating,
            "혼잡도(오전)": congestion_m,
            "혼잡도(점심)": congestion_l,
            "혼잡도(저녁)": congestion_e,
            "거리(km)": haversine(lat_user, lon_user, lat, lon)
        }])
        st.session_state["restaurants"] = pd.concat([df, new_row], ignore_index=True)
        st.success(f"✅ '{name}' 음식점이 추가되었습니다! (지도 새로고침 시 반영)")

# -----------------------------
# 📊 요약 시각화
# -----------------------------
st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📈 카테고리별 평균 평점")
    avg_ratings = df.groupby("카테고리")["평점"].mean().reset_index()
    st.bar_chart(avg_ratings.set_index("카테고리"))

with col_b:
    st.subheader("👥 시간대별 평균 혼잡도")
    avg_congestion = {
        "오전": df["혼잡도(오전)"].mean(),
        "점심": df["혼잡도(점심)"].mean(),
        "저녁": df["혼잡도(저녁)"].mean()
    }
    st.bar_chart(pd.Series(avg_congestion))
