import streamlit as st
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# 全局记忆
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

# 页面样式
st.set_page_config(layout="wide")
st.title("航线规划（3D地图）")

# 左侧 + 右侧布局
col_left, col_right = st.columns([1, 3])

with col_left:
    st.subheader("坐标信息")
    a_lat = st.number_input("A纬度", value=st.session_state.A[0], format="%.6f")
    a_lon = st.number_input("A经度", value=st.session_state.A[1], format="%.6f")
    b_lat = st.number_input("B纬度", value=st.session_state.B[0], format="%.6f")
    b_lon = st.number_input("B经度", value=st.session_state.B[1], format="%.6f")

    # 绿色按钮（和截图一致）
    if st.button("A点已设", type="primary"):
        st.session_state.A = (a_lat, a_lon)
    if st.button("B点已设", type="primary"):
        st.session_state.B = (b_lat, b_lon)
