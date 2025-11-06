import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="🍽️ 한국 음식점 데이터 대시보드",
    page_icon="🍜",
    layout="wide"
)

# --- 데이터 불러오기 ---
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

data = load_data("data/restaurants.csv")

# --- 사이드바 ---
st.sidebar.title("🍴 필터 설정")
st.sidebar.markdown("원하는 **지역**과 **음식 종류**를 선택하세요.")

locations = st.sidebar.multiselect(
    "📍 지역 선택",
    sorted(data["location"].unique()),
    default=data["location"].unique()
)

categories = st.sidebar.multiselect(
    "🍱 음식 종류 선택",
    sorted(data["category"].unique()),
    default=data["category"].unique()
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 데이터는 예시용으로 작성되었습니다.")

# --- 필터 적용 ---
filtered = data[(data["location"].isin(locations)) & (data["category"].isin(categories))]

# --- 타이틀 ---
st.markdown(
    """
    <h1 style='text-align: center; color: #FF6347;'>
        🍜 한국 음식점 데이터 시각화 대시보드
    </h1>
    <p style='text-align:center; color:gray'>
        음식 종류별 평점, 지역별 분포, 지도 시각화를 한눈에!
    </p>
    """,
    unsafe_allow_html=True
)

# --- 지표 카드 ---
col1, col2, col3 = st.columns(3)
col1.metric("총 음식점 수", f"{len(filtered):,} 곳")
col2.metric("평균 평점", f"{filtered['rating'].mean():.2f} ⭐")
col3.metric("평균 가격대", f"{filtered['price_range'].mode()[0]}")

st.divider()

# --- 1. 지도 시각화 ---
st.subheader("🗺️ 음식점 위치 지도")
st.map(filtered, size=100)

# --- 2. 카테고리별 평균 평점 ---
st.subheader("📊 음식 종류별 평균 평점")
fig1 = px.bar(
    filtered.groupby("category")["rating"].mean().sort_values(ascending=False).reset_index(),
    x="category",
    y="rating",
    color="category",
    color_discrete_sequence=px.colors.qualitative.Bold,
    text_auto=".2f"
)
fig1.update_layout(
    xaxis_title="음식 종류",
    yaxis_title="평균 평점",
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig1, use_container_width=True)

# --- 3. 지역별 비율 ---
st.subheader("🍕 지역별 음식점 비율")
fig2 = px.pie(
    filtered,
    names="location",
    title="지역별 음식점 분포",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
st.plotly_chart(fig2, use_container_width=True)

# --- 4. 음식점 목록 ---
st.subheader("📋 음식점 목록")
st.dataframe(filtered, use_container_width=True)

# --- 푸터 ---
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray'>
        Made with ❤️ by <b>Streamlit</b> | 한국 음식점 데이터 예시 대시보드
    </p>
    """,
    unsafe_allow_html=True
)
