import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="🍽️ 서울 음식점 시각화 대시보드",
    layout="wide",
    page_icon="🍴",
)

# --- 데이터 직접 포함 ---
@st.cache_data
def load_data():
    data = {
        "name": [
            "한식당 서울", "이탈리안 하우스", "스시야 도쿄", "분식나라",
            "인도커리집", "타코가게", "카페 모닝", "중화반점",
            "치킨천국", "비건그린"
        ],
        "category": [
            "한식", "양식", "일식", "분식", "아시아음식",
            "멕시코음식", "카페", "중식", "패스트푸드", "건강식"
        ],
        "price_range": [
            "₩₩", "₩₩₩", "₩₩₩", "₩", "₩₩",
            "₩₩", "₩", "₩₩", "₩", "₩₩₩"
        ],
        "location": ["서울"] * 10,
        "rating": [4.5, 4.2, 4.8, 3.9, 4.3, 4.1, 4.6, 4.0, 4.4, 4.7],
        "lat": [
            37.5665, 37.5650, 37.5700, 37.5685, 37.5610,
            37.5635, 37.5580, 37.5620, 37.5670, 37.5590
        ],
        "lon": [
            126.9780, 126.9820, 126.9830, 126.9760, 126.9900,
            126.9740, 126.9720, 126.9810, 126.9750, 126.9770
        ],
    }
    return pd.DataFrame(data)

df = load_data()

# --- 제목 ---
st.title("🍽️ 서울 음식점 시각화 대시보드")
st.caption("서울 내 주요 음식점들의 정보를 시각화한 Streamlit 대시보드입니다.")

# --- 사이드바 필터 ---
st.sidebar.header("🔍 필터")
categories = st.sidebar.multiselect(
    "음식 종류 선택", 
    sorted(df["category"].unique()), 
    default=df["category"].unique()
)

# --- 필터 적용 ---
filtered = df[df["category"].isin(categories)]

# --- 상단 요약 ---
st.markdown("### 📊 요약 통계")
col_a, col_b, col_c = st.columns(3)
col_a.metric("총 음식점 수", f"{len(filtered)}개")
col_b.metric("평균 평점", f"{filtered['rating'].mean():.2f}")
col_c.metric("최고 평점", f"{filtered['rating'].max():.1f}")

st.divider()

# --- 상단 2열: 표 + 지도 ---
col1, col2 = st.columns([1.1, 2])

# 표 + 음식 종류별 평균 평점
with col1:
    st.subheader("📋 음식점 목록")
    st.dataframe(
        filtered[["name", "category", "price_range", "rating"]],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("⭐ 음식 종류별 평균 평점")
    avg_rating = filtered.groupby("category")["rating"].mean().sort_values(ascending=True)
    fig_bar = px.bar(
        avg_rating,
        x=avg_rating.values,
        y=avg_rating.index,
        orientation="h",
        color=avg_rating.values,
        color_continuous_scale="sunset",
        labels={"x": "평균 평점", "y": "음식 종류"},
        title="음식 종류별 평균 평점 비교",
    )
    fig_bar.update_layout(showlegend=False, height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

# 지도
with col2:
    st.subheader("🗺️ 음식점 위치 지도 (서울 중심 확대)")
    fig_map = px.scatter_mapbox(
        filtered,
        lat="lat",
        lon="lon",
        color="category",
        size="rating",
        hover_name="name",
        hover_data={
            "rating": True,
            "price_range": True,
            "lat": False,
            "lon": False,
        },
        color_discrete_sequence=px.colors.qualitative.Pastel,
        zoom=12,  # 🔍 확대 레벨 조정
        center={"lat": 37.5665, "lon": 126.9780},  # 서울 시청 중심
        height=650,
        title="서울 음식점 분포 지도"
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0, "t":40, "l":0, "b":0})
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# --- 하단 시각화 ---
col3, col4 = st.columns(2)

# 가격대별 비율 파이차트
with col3:
    st.subheader("💰 가격대별 비율")
    price_counts = filtered["price_range"].value_counts()
    fig_pie = px.pie(
        values=price_counts.values,
        names=price_counts.index,
        color_discrete_sequence=px.colors.sequential.RdPu,
        hole=0.4,
        title="가격대별 음식점 분포"
    )
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

# 음식점 평점 상위 3
with col4:
    st.subheader("🏆 평점 상위 3 음식점")
    top3 = filtered.nlargest(3, "rating")[["name", "category", "rating"]]
    st.table(top3.set_index("name"))

st.divider()
st.markdown("📍 *데이터는 예시용이며 실제 음식점 정보와 다를 수 있습니다.*")
