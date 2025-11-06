import streamlit as st
import pandas as pd

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

st.title("🍽️ 한국 음식점 데이터 시각화 대시보드")

# 데이터 불러오기
data = load_data("data/restaurants.csv")

# 사이드바 필터
locations = st.sidebar.multiselect("지역 선택", sorted(data["location"].unique()), default=data["location"].unique())
categories = st.sidebar.multiselect("음식 종류 선택", sorted(data["category"].unique()), default=data["category"].unique())

# 필터 적용
filtered = data[(data["location"].isin(locations)) & (data["category"].isin(categories))]

st.subheader("📊 음식점 목록")
st.dataframe(filtered)

st.subheader("⭐ 평균 평점 비교")
st.bar_chart(filtered.groupby("category")["rating"].mean())
