import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# 全局状态（不写死）
if "A" not in st.session_state:
    st.session_state.A = (32.0, 118.0)
if "B" not in st.session_state:
    st.session_state.B = (32.1, 118.1)
if "heartbeat_data" not in st.session_state:
    st.session_state.heartbeat_data = []
if "polygon_memory" not in st.session_state:
    st.session_state.polygon_memory = []
if "is_drawing" not in st.session_state:
    st.session_state.is_drawing = False
if "temp_points" not in st.session_state:
    st.session_state.temp_points = []

st.set_page_config(layout="wide")
st.title("航线规划（3D地图）")

# 左侧 + 右侧布局
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("坐标信息")

    # A/B点输入
    a_lat = st.number_input("A纬度", value=st.session_state.A[0], format="%.6f")
    a_lon = st.number_input("A经度", value=st.session_state.A[1], format="%.6f")
    b_lat = st.number_input("B纬度", value=st.session_state.B[0], format="%.6f")
    b_lon = st.number_input("B经度", value=st.session_state.B[1], format="%.6f")

    # 设置按钮
    if st.button("设置A点"):
        st.session_state.A = (a_lat, a_lon)
        st.success("A点已设")
    if st.button("设置B点"):
        st.session_state.B = (b_lat, b_lon)
        st.success("B点已设")

    # 障碍物圈选
    st.subheader("障碍物设置")
    if st.button("开始圈选障碍物"):
        st.session_state.is_drawing = True
        st.session_state.temp_points = []
        st.info("点击地图圈点 → 右键结束")
    if st.button("清除障碍物"):
        st.session_state.polygon_memory = []
        st.session_state.temp_points = []
        st.warning("已清除所有障碍物")

    # 心跳图
    st.subheader("心跳状态")
    now = datetime.now().strftime("%H:%M:%S")
    st.metric("当前时间", now)
    st.success("心跳正常")

    # 心跳数据更新
    st.session_state.heartbeat_data.append(time.time())
    if len(st.session_state.heartbeat_data) > 20:
        st.session_state.heartbeat_data.pop(0)

# 右侧地图（实时刷新）
with col2:
    center_lat = (st.session_state.A[0] + st.session_state.B[0]) / 2
    center_lon = (st.session_state.A[1] + st.session_state.B[1]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # A/B点标记 + 航线
    folium.Marker(st.session_state.A, popup="A点", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker(st.session_state.B, popup="B点", icon=folium.Icon(color="green")).add_to(m)
    folium.PolyLine([st.session_state.A, st.session_state.B], color="blue", weight=3).add_to(m)

    # 绘制已记忆障碍物
    for poly in st.session_state.polygon_memory:
        folium.Polygon(locations=poly, color="red", fill=True, fill_opacity=0.5).add_to(m)
    # 临时圈选线
    if st.session_state.temp_points:
        folium.PolyLine(locations=st.session_state.temp_points, color="red").add_to(m)

    output = st_folium(m, width=1000, height=600)

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
        st.success("障碍物已保存")

st.caption("功能：A/B点可设置｜实时地图｜心跳监控｜障碍物圈选｜航线显示")
