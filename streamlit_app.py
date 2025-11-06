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
        filtered[["name", "category", "price_range", "location", "rating"]],
        use_container_width=True,
        hide_index=True,
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

with col2:
    st.subheader("🗺️ 음식점 위치 지도")
    # 지도 시각화
    try:
        fig_map = px.scatter_mapbox(
            filtered,
            lat="lat",
            lon="lon",
            color="category",
            size="rating",
            hover_name="name",
            hover_data={"location": True, "rating": True, "price_range": True, "lat": False, "lon": False},
            color_discrete_sequence=px.colors.qualitative.Pastel,
            zoom=6,
            height=650,
            title="지역별 음식점 분포",
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0, "t":40, "l":0, "b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    except ValueError:
        st.error("지도를 표시하는 중 오류가 발생했습니다. lat/lon 데이터가 올바른지 확인해주세요.")

st.markdown("---")
st.markdown("📊 **총 음식점 수:** {}개 | ⭐ **평균 평점:** {:.2f}".format(len(filtered), filtered["rating"].mean()))
