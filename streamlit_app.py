import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🍽️ 한국 음식점 시각화 대시보드", layout="wide", page_icon="🍴")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    # 숫자형 변환 (지도에서 오류 방지)
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    return df

data = load_data("data/restaurants.csv")

st.title("🍽️ 한국 음식점 시각화 대시보드")
st.caption("전국 주요 도시의 음식점 데이터를 기반으로 한 시각화 대시보드입니다.")

# 사이드바 필터
st.sidebar.header("🔍 필터")
locations = st.sidebar.multiselect("지역 선택", sorted(data["location"].unique()), default=data["location"].unique())
categories = st.sidebar.multiselect("음식 종류 선택", sorted(data["category"].unique()), default=data["category"].unique())

filtered = data[(data["location"].isin(locations)) & (data["category"].isin(categories))]

# 데이터 없을 때 메시지 처리
if filtered.empty:
    st.warning("⚠️ 선택한 조건에 맞는 음식점이 없습니다.")
    st.stop()

col1, col2 = st.columns([1.1, 2])

with col1:
    st.subheader("📋 음식점 목록")
    st.dataframe(
        fi
