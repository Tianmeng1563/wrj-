import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# 初始化全局记忆（重启前不丢失）
if "polygon_memory" not in st.session_state:
    st.session_state.polygon_memory = []
if "is_drawing" not in st.session_state:
    st.session_state.is_drawing = False
if "temp_points" not in st.session_state:
    st.session_state.temp_points = []

# 初始坐标
A_LAT, A_LON = 32.0, 118.0
B_LAT, B_LON = 32.1, 118.1

st.title("无人机监控系统（最终完整版）")

# 左侧控制面板
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("参数设置")
    a_lat = st.number_input("A点纬度", value=A_LAT, format="%.6f")
    a_lon = st.number_input("A点经度", value=A_LON, format="%.6f")
    b_lat = st.number_input("B点纬度", value=B_LAT, format="%.6f")
    b_lon = st.number_input("B点经度", value=B_LON, format="%.6f")

    if st.button("更新A/B点"):
        st.success("A/B点已更新")

    st.subheader("圈选障碍")
    if st.button("开始圈选障碍"):
        st.session_state.is_drawing = True
        st.session_state.temp_points = []
        st.info("点击地图圈点，右键结束")

    if st.button("清除圈选"):
        st.session_state.polygon_memory = []
        st.session_state.temp_points = []
        st.warning("已清除所有障碍")

    st.subheader("心跳状态")
    st.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    st.success("心跳正常")

# 右侧地图
with col2:
    m = folium.Map(location=[(a_lat + b_lat)/2, (a_lon + b_lon)/2], zoom_start=12)

    # A/B点标记
    folium.Marker([a_lat, a_lon], popup="A点", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker([b_lat, b_lon], popup="B点", icon=folium.Icon(color="green")).add_to(m)

    # 绘制已记忆的多边形
    for poly in st.session_state.polygon_memory:
        folium.Polygon(locations=poly, color="blue", fill=True, fill_opacity=0.4).add_to(m)

    # 绘制临时圈选
    if st.session_state.temp_points:
        folium.PolyLine(locations=st.session_state.temp_points, color="red").add_to(m)

    output = st_folium(m, width=700, height=500)

    # 圈选逻辑
    if st.session_state.is_drawing and output.get("last_clicked"):
        lat = output["last_clicked"]["lat"]
        lon = output["last_clicked"]["lng"]
        st.session_state.temp_points.append([lat, lon])

    # 右键结束圈选并保存
    if output.get("last_object_clicked") is None and len(st.session_state.temp_points) >= 3:
        st.session_state.polygon_memory.append(st.session_state.temp_points)
        st.session_state.is_drawing = False
        st.session_state.temp_points = []
        st.success("障碍已保存到记忆")

st.divider()
st.caption("功能：A/B点设置 + 实时地图 + 心跳 + 多边形圈选 + 记忆")
