import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="🍽️ 음식점 위치 및 평점 대시보드",
    page_icon="🍴",
    layout="wide"
)

# --- 2. 데이터 로딩 ---
@st.cache_data
def load_data():
    url = "https://www.data.go.kr/tcs/dss/selectFileDataDetailView.do?publicDataPk=15096283"
    df = pd.read_csv("https://raw.githubusercontent.com/Datamanim/datarepo/main/restaurant/restaurant.csv")
    df = df.rename(columns={
        '위도': 'lat', 
        '경도': 'lon', 
        '업태구분명': 'category', 
        '사업장명': 'name'
    })
    # 평점 컬럼 임의 생성 (1~5)
    np.random.seed(42)
    df['rating'] = np.random.uniform(3.0, 5.0, size=len(df)).round(1)
    # NaN이나 이상치 제거
    df = df.dropna(subset=['lat', 'lon'])
    return df

data = load_data()

# --- 3. 사이드바 UI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/857/857681.png", width=100)
    st.title("🍴 음식점 필터")
    
    categories = sorted(data['category'].dropna().unique().tolist())
    selected_cat = st.selectbox("음식 종류 선택", categories)
    
    min_rating = st.slider("최소 평점 선택", 3.0, 5.0, 4.0, 0.1)
    
    k_clusters = st.slider("클러스터 개수 (K)", 1, 10, 1)
    
    show_raw = st.checkbox("필터링된 데이터 보기")

# --- 4. 데이터 필터링 ---
filtered = data[(data['category'] == selected_cat) & (data['rating'] >= min_rating)]

st.title(f"📍 {selected_cat} 음식점 위치 및 평점 분석")
st.markdown(f"**총 {len(filtered)}개** 음식점이 평점 {min_rating} 이상입니다.")

# --- 5. 지도 시각화 ---
if not filtered.empty:
    st.subheader("🗺️ 지도 시각화")
    if k_clusters > 1:
        # K-Means 군집화
        kmeans = KMeans(n_clusters=k_clusters, n_init=10, random_state=42)
        filtered['cluster'] = kmeans.fit_predict(filtered[['lat', 'lon']])
        # 클러스터별 색상 매핑
        cluster_colors = [
            "#FF0000", "#0000FF", "#00FF00", "#FFFF00", "#00FFFF",
            "#FF00FF", "#C0C0C0", "#800000", "#008000", "#000080"
        ]
        filtered['color'] = filtered['cluster'].apply(lambda x: cluster_colors[x % len(cluster_colors)])
        st.map(filtered[['lat', 'lon']])
        st.caption(f"총 {k_clusters}개의 군집으로 분류됨")
    else:
        st.map(filtered[['lat', 'lon']])

    # --- 6. 통계 시각화 ---
    st.subheader("🍴 지역별 음식점 분포")
    region_counts = filtered['소재지도로명주소'].str.split().str[1].value_counts().head(10)
    st.bar_chart(region_counts)

    st.subheader("⭐ 평점 분포")
    rating_counts = filtered['rating'].value_counts().sort_index()
    st.bar_chart(rating_counts)

    # --- 7. 원본 데이터 표시 ---
    if show_raw:
        st.subheader("📊 원본 데이터 (필터 적용됨)")
        st.dataframe(filtered[['name', 'category', 'rating', 'lat', 'lon', '소재지도로명주소']])
else:
    st.warning("조건에 맞는 음식점이 없습니다.")
