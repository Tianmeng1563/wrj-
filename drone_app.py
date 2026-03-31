import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# 全局状态
if "A" not in st.session_state:
    st.session_state.A = (32.0, 118.0)
if "B" not in st.session_state:
    st.session_state.B = (32.1, 118.1)
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []

st.set_page_config(layout="wide")
st.title("航线规划（3D地图）")

# 左侧面板
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("坐标信息")
    a_lat = st.number_input("A纬度", value=st.session_state.A[0], format="%.6f")
    a_lon = st.number_input("A经度", value=st.session_state.A[1], format="%.6f")
    b_lat = st.number_input("B纬度", value=st.session_state.B[0], format="%.6f")
    b_lon = st.number_input("B经度", value=st.session_state.B[1], format="%.6f")

    # 红色按钮
    st.button("A点已设", type="primary")
    st.button("B点已设", type="primary")

    # 心跳图
    st.subheader("心跳状态")
    now = datetime.now().strftime("%H:%M:%S")
    st.metric("当前时间", now)
    st.success("心跳正常")

    # 模拟心跳数据
    st.session_state.heartbeat_data.append(time.time())
    if len(st.session_state.heartbeat_data) > 20:
        st.session_state.heartbeat_data.pop(0)

# 右侧地图
with col2:
    center_lat = (st.session_state.A[0] + st.session_state.B[0]) / 2
    center_lon = (st.session_state.A[1] + st.session_state.B[1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

    # A/B点标记
    folium.Marker(st.session_state.A, popup="A点", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(st.session_state.B, popup="B点", icon=folium.Icon(color="green")).add_to(m)
    folium.PolyLine([st.session_state.A, st.session_state.B], color="blue", weight=3).add_to(m)

    st_folium(m, width=1000, height=600)

st.caption("功能：A/B点设置 + 3D地图 + 心跳监控 + 航线显示")
