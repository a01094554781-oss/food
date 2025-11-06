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

# --- 레이아웃: 2열 구성 ---
col1, col2 = st.columns([1.1, 2])

# --- 왼쪽: 표 + 바 그래프 ---
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

# --- 오른쪽: 지도 ---
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

# --- 하단 요약 ---
st.markdown("---")
st.markdown(
    f"📊 **총 음식점 수:** {len(filtered)}개 | ⭐ **평균 평점:** {filtered['rating'].mean():.2f}"
)
