import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="🍽️ 한국 음식점 시각화 대시보드",
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
        "location": [
            "서울", "부산", "서울", "대구", "서울",
            "인천", "서울", "광주", "서울", "대전"
        ],
        "rating": [4.5, 4.2, 4.8, 3.9, 4.3, 4.1, 4.6, 4.0, 4.4, 4.7],
        "lat": [
            37.5665, 35.1796, 37.5700, 35.8714, 37.5610,
            37.4563, 37.5580, 35.1595, 37.5630, 36.3504
        ],
        "lon": [
            126.9780, 129.0756, 126.9820, 128.6014, 126.9900,
            126.7052, 126.9720, 126.8526, 126.9750, 127.3845
        ],
    }
    return pd.DataFrame(data)

df = load_data()

# --- 제목 ---
st.title("🍽️ 한국 음식점 시각화 대시보드")
st.caption("전국 주요 도시의 음식점 정보를 시각화한 Streamlit 대시보드입니다.")

# --- 사이드바 필터 ---
st.sidebar.header("🔍 필터")
locations = st.sidebar.multiselect(
    "지역 선택", 
    sorted(df["location"].unique()), 
    default=df["location"].unique()
)
categories = st.sidebar.multiselect(
    "음식 종류 선택", 
    sorted(df["category"].unique()), 
    default=df["category"].unique()
)

# --- 필터 적용 ---
filtered = df[
    (df["location"].isin(locations)) &
    (df["category"].isin(categories))
]

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
        filtered[["name", "category", "price_range", "location", "rating"]],
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
    st.subheader("🗺️ 음식점 위치 지도")
    fig_map = px.scatter_mapbox(
        filtered,
        lat="lat",
        lon="lon",
        color="category",
        size="rating",
        hover_name="name",
        hover_data={
            "location": True,
            "rating": True,
            "price_range": True,
            "lat": False,
            "lon": False,
        },
        color_discrete_sequence=px.colors.qualitative.Pastel,
        zoom=6,
        height=650,
        title="지역별 음식점 분포"
    )
    fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0, "t":40, "l":0, "b":0})
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# --- 하단 2열: 추가 시각화 ---
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

# 도시별 평균 평점 비교
with col4:
    st.subheader("🏙️ 도시별 평균 평점 비교")
    city_rating = filtered.groupby("location")["rating"].mean().sort_values(ascending=False)
    fig_city = px.bar(
        city_rating,
        x=city_rating.index,
        y=city_rating.values,
        color=city_rating.values,
        color_continuous_scale="Agsunset",
        labels={"x": "도시", "y": "평균 평점"},
        title="도시별 평균 평점 비교",
    )
    fig_city.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_city, use_container_width=True)

st.divider()
st.markdown("📍 *데이터는 예시용이며 실제 음식점 정보와 다를 수 있습니다.*")
