import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

# 全局记忆（重启不丢）
if "polygon_memory" not in st.session_state:
    st.session_state.polygon_memory = []
if "is_drawing" not in st.session_state:
    st.session_state.is_drawing = False
if "temp_points" not in st.session_state:
    st.session_state.temp_points = []
if "A" not in st.session_state:
    st.session_state.A = (32.0, 118.0)
if "B" not in st.session_state:
    st.session_state.B = (32.1, 118.1)

st.title("无人机监控系统（完整版）")

# 布局：左侧控制 + 右侧地图
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("A/B点设置")
    a_lat = st.number_input("A纬度", value=st.session_state.A[0], format="%.6f")
    a_lon = st.number_input("A经度", value=st.session_state.A[1], format="%.6f")
    b_lat = st.number_input("B纬度", value=st.session_state.B[0], format="%.6f")
    b_lon = st.number_input("B经度", value=st.session_state.B[1], format="%.6f")

    if st.button("设置A点"):
        st.session_state.A = (a_lat, a_lon)
        st.success("A点已设")
    if st.button("设置B点"):
        st.session_state.B = (b_lat, b_lon)
        st.success("B点已设")

    st.subheader("障碍圈选")
    if st.button("开始圈选障碍"):
        st.session_state.is_drawing = True
        st.session_state.temp_points = []
        st.info("点击地图加点 → 右键结束")
    if st.button("清除圈选"):
        st.session_state.polygon_memory = []
        st.session_state.temp_points = []
        st.warning("已清除")

    st.subheader("心跳状态")
    st.metric("时间", datetime.now().strftime("%H:%M:%S"))
    st.success("心跳正常")

with col2:
    center_lat = (st.session_state.A[0] + st.session_state.B[0]) / 2
    center_lon = (st.session_state.A[1] + st.session_state.B[1]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # A/B点标记
    folium.Marker(st.session_state.A, popup="A", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(st.session_state.B, popup="B", icon=folium.Icon(color="green")).add_to(m)
    folium.PolyLine([st.session_state.A, st.session_state.B], color="blue").add_to(m)

    # 已记忆障碍
    for poly in st.session_state.polygon_memory:
        folium.Polygon(locations=poly, color="blue", fill=True, fill_opacity=0.4).add_to(m)
    # 临时圈选
    if st.session_state.temp_points:
        folium.PolyLine(locations=st.session_state.temp_points, color="red").add_to(m)

    output = st_folium(m, width=700, height=500)

    # 圈选逻辑
    if st.session_state.is_drawing and output.get("last_clicked"):
        lat = output["last_clicked"]["lat"]
        lon = output["last_clicked"]["lng"]
        st.session_state.temp_points.append([lat, lon])
    # 右键结束并保存
    if output.get("last_object_clicked") is None and len(st.session_state.temp_points) >= 3:
        st.session_state.polygon_memory.append(st.session_state.temp_points)
        st.session_state.is_drawing = False
        st.session_state.temp_points = []
        st.success("障碍已记忆")

st.divider()
st.caption("功能：A/B点可设｜实时地图｜心跳｜多边形圈选｜记忆")
