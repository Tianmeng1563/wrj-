import streamlit as st
import pydeck as pdk
import time
import random
import pandas as pd

st.set_page_config(page_title="无人机智能化应用", layout="wide")

# 初始化状态
if 'latA' not in st.session_state:
    st.session_state.latA = 32.232200
if 'lonA' not in st.session_state:
    st.session_state.lonA = 118.749000
if 'latB' not in st.session_state:
    st.session_state.latB = 32.234300
if 'lonB' not in st.session_state:
    st.session_state.lonB = 118.749000
if 'a_set' not in st.session_state:
    st.session_state.a_set = False
if 'b_set' not in st.session_state:
    st.session_state.b_set = False

# 侧边栏
with st.sidebar:
    st.title("导航")
    st.subheader("功能页面")
    page = st.radio("", ["航线规划", "飞行监控"])
    st.subheader("坐标系")
    coord = st.radio("", ["GCJ-02(高德/百度)", "WGS-84"])
    st.divider()
    st.subheader("系统状态")
    if st.session_state.a_set:
        st.success("A点已设")
    else:
        st.success("A点未设")
    if st.session_state.b_set:
        st.success("B点已设")
    else:
        st.success("B点未设")

# 航线规划
if page == "航线规划":
    st.title("航线规划（3D地图）")
    st.subheader("坐标信息")

    col_map, col_ctrl = st.columns([3, 1])

    with col_ctrl:
        st.subheader("控制面板")
        st.session_state.latA = st.number_input("起点A纬度", value=st.session_state.latA, format="%.6f")
        st.session_state.lonA = st.number_input("起点A经度", value=st.session_state.lonA, format="%.6f")
        st.session_state.latB = st.number_input("终点B纬度", value=st.session_state.latB, format="%.6f")
        st.session_state.lonB = st.number_input("终点B经度", value=st.session_state.lonB, format="%.6f")
        height = st.slider("飞行高度(m)", 0, 100, 46)

        if st.button("设置A点"):
            st.session_state.a_set = True
        if st.button("设置B点"):
            st.session_state.b_set = True

    with col_map:
        # 动态地图
        view_state = pdk.ViewState(
            latitude=(st.session_state.latA + st.session_state.latB) / 2,
            longitude=(st.session_state.lonA + st.session_state.lonB) / 2,
            zoom=17,
            pitch=45,
            bearing=0
        )

        # A点
        layer_a = pdk.Layer(
            "ScatterplotLayer",
            data=[{"position": [st.session_state.lonA, st.session_state.latA], "color": [255,0,0], "radius": 15}],
            get_position="position",
            get_color="color",
            get_radius="radius",
        )

        # B点
        layer_b = pdk.Layer(
            "ScatterplotLayer",
            data=[{"position": [st.session_state.lonB, st.session_state.latB], "color": [0,255,0], "radius": 15}],
            get_position="position",
            get_color="color",
            get_radius="radius",
        )

        # 航线
        line_layer = pdk.Layer(
            "LineLayer",
            data=[{"path": [[st.session_state.lonA, st.session_state.latA], [st.session_state.lonB, st.session_state.latB]]}],
            get_path="path",
            get_color=[0,0,255],
            get_width=3,
        )

        st.pydeck_chart(pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            initial_view_state=view_state,
            layers=[layer_a, layer_b, line_layer],
            height=500
        ))

# 飞行监控（心跳图）
else:
    st.title("飞行监控（心跳包）")
    hb_time = st.empty()
    hb_lat = st.empty()
    hb_lon = st.empty()
    hb_height = st.empty()
    hb_battery = st.empty()
    hb_status = st.empty()
    chart = st.empty()

    data = []
    while True:
        t = time.strftime("%H:%M:%S")
        lat = round(st.session_state.latA + random.uniform(-0.0003, 0.0003), 6)
        lon = round(st.session_state.lonA + random.uniform(-0.0003, 0.0003), 6)
        h = random.randint(40, 50)
        bat = random.randint(80, 100)

        hb_time.metric("时间", t)
        hb_lat.metric("纬度", f"{lat}")
        hb_lon.metric("经度", f"{lon}")
        hb_height.metric("高度", f"{h}m")
        hb_battery.metric("电量", f"{bat}%")
        hb_status.success("连接正常")

        data.append({"time": t, "高度": h, "电量": bat})
        if len(data) > 20:
            data.pop(0)
        df = pd.DataFrame(data)
        chart.line_chart(df, x="time", y=["高度", "电量"])

        time.sleep(1)
