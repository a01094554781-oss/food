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

# --- 2. 데이터 로딩 함수 ---
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    # 컬럼명 표준화
    df = df.rename(columns={
        '위도': 'lat',
        '경도': 'lon',
        '업태구분명': 'category',
        '사업장명': 'name'
    })
    # 평점 컬럼이 없으면 샘플로 생성
    if 'rating' not in df.columns:
        np.random.seed(42)
        df['rating'] = np.random.uniform(3.0, 5.0, size=len(df)).round(1)
    # 위도/경도 누락 행 제거
    df = df.dropna(subset=['lat', 'lon'])
    return df

# --- 3. 사이드바 UI ---
with st.sidebar:
    st.title("🍴 필터")
    categories = ['한식', '중식', '일식', '양식', '카페/디저트']
    selected_cat = st.selectbox("음식 종류 선택", categories)
    min_rating = st.slider("최소 평점", 3.0, 5.0, 4.0, 0.1)
    k_clusters = st.slider("클러스터 개수 (K)", 1, 10, 1)
    show_raw = st.checkbox("원본 데이터 보기")

# --- 4. 메인 화면 ---
st.title("📍 음식점 위치·평점 분석")
st.markdown(f"**선택된 음식 종류**: {selected_cat}  |  **평점 ≥ {min_rating}**")

data = load_data("data/restaurants.csv")

# 필터 적용
filtered = data[(data['category'] == selected_cat) & (data['rating'] >= min_rating)]

if filtered.empty:
    st.warning("조건에 맞는 음식점이 없습니다.")
else:
    st.subheader(f"총 {len(filtered)}개 음식점")

    # 지도 시각화
    st.subheader("🗺️ 지도 시각화")
    if k_clusters > 1:
        kmeans = KMeans(n_clusters=k_clusters, random_state=42)
        filtered['cluster'] = kmeans.fit_predict(filtered[['lat', 'lon']])
        cluster_colors = [
            "#FF0000", "#0000FF", "#00FF00", "#FFFF00",
            "#00FFFF", "#FF00FF", "#C0C0C0", "#800000", "#008000", "#000080"
        ]
        filtered['color'] = filtered['cluster'].apply(lambda x: cluster_colors[x % len(cluster_colors)])
        st.map(filtered[['lat', 'lon']])
        st.caption(f"{k_clusters}개 군집으로 분류됨")
    else:
        st.map(filtered[['lat', 'lon']])

    # 통계 시각화: 음식점 분포
    st.subheader("🍴 카테고리 내 음식점 분포 (평점 필터 적용됨)")
    count_by_rating = filtered['rating'].value_counts().sort_index()
    st.bar_chart(count_by_rating)

    # 원본 데이터 보기
    if show_raw:
        st.subheader("📊 원본 데이터 (필터 적용됨)")
        st.dataframe(filtered[['name', 'category', 'rating', 'lat', 'lon']])

