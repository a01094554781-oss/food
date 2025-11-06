import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

st.set_page_config(
    page_title="음식점 위치 & 평점 대시보드",
    page_icon="🍽️",
    layout="wide"
)

TEXTS = {
    'ko': {
        'lang_select': '언어 선택',
        'main_title': '📍 전국 음식점 위치 및 분석',
        'main_desc': '음식점 위치, 카테고리, 평점을 기반으로 시각화합니다.',
        'filter_header': '필터 설정',
        'category_select': '음식 종류 선택:',
        'k_slider_label': '클러스터 개수 (K):',
        'k_slider_help': 'K=1이면 클러스터링 없음.',
        'show_data_label': '원본 데이터 보기',
        'no_data_warn': '선택된 필터에 데이터가 없습니다.'
    },
    'en': {
        # … 영어버전 …
    }
}

if 'lang' not in st.session_state:
    st.session_state.lang = 'ko'
lang = st.session_state.lang

with st.sidebar:
    lang_options = {'한국어':'ko', 'English':'en'}
    selected = st.radio(TEXTS['ko']['lang_select'], list(lang_options.keys()))
    st.session_state.lang = lang_options[selected]
    lang = st.session_state.lang

    st.header(TEXTS[lang]['filter_header'])
    # 음식 카테고리 선택
    categories = ['한식','중식','일식','분식','카페/디저트']
    category = st.selectbox(TEXTS[lang]['category_select'], categories)
    k_clusters = st.slider(TEXTS[lang]['k_slider_label'], 1, 10, 1, help=TEXTS[lang]['k_slider_help'])
    show_raw = st.checkbox(TEXTS[lang]['show_data_label'])

st.title(TEXTS[lang]['main_title'])
st.markdown(TEXTS[lang]['main_desc'])

@st.cache_data
def load_data():
    df = pd.read_csv('food_restaurants_all.csv', encoding='utf-8')
    # 좌표 변환, 카테고리 필터 등 전처리
    return df

data = load_data()

# 카테고리 필터
filtered = data[data['category']==category]

if filtered.empty:
    st.warning(TEXTS[lang]['no_data_warn'])
else:
    st.write(f"선택된 음식점 개수: **{len(filtered)}**")
    
    if 'lat' in filtered.columns and 'lon' in filtered.columns:
        if k_clusters > 1:
            kmeans = KMeans(n_clusters=k_clusters, random_state=42)
            filtered['cluster'] = kmeans.fit_predict(filtered[['lat','lon']])
            filtered['color'] = filtered['cluster'].apply(lambda x: ...)
            st.map(filtered[['lat','lon','color']])
        else:
            st.map(filtered[['lat','lon']])
    
    st.subheader("음식점 카테고리 분포")
    cat_counts = filtered['category'].value_counts().reset_index()
    cat_counts.columns = ['category','count']
    st.bar_chart(cat_counts.set_index('category'))
    
    if show_raw:
        st.subheader("원본 데이터")
        st.dataframe(filtered)

