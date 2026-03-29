import streamlit as st
import pydeck as pdk
import time
import random
import pandas as pd

# 全局深色主题配置
st.set_page_config(page_title="无人机智能化应用", layout="wide")
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e2e;
        color: #ffffff;
    }
    .sidebar .block-container {
        background-color: #2d2d3f;
    }
    .stButton>button {
        background-color: #2d2d3f;
        color: white;
        border: 1px solid #444;
    }
    .stButton>button:hover {
        background-color: #3d3d5f;
    }
    .stSuccess {
        background-color: #2e7d32;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------- 坐标系转换 ----------------------
def wgs84_to_gcj02(lat, lon):
    pi = 3.14159265358979323846
    a = 6378245.0
    ee = 0.00669342162296594323

    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * (abs(x))**0.5
        ret += (20.0 * (6.0 * (x * pi / 180.0)) + 20.0 * (6.0 * (y * pi / 180.0))) / 2.0
        ret += (20.0 * (6.0 * (x * pi / 180.0))) / 2.0
        ret += (40.0 * (6.0 * (x * pi / 180.0))) / 3.0
        ret += (160.0 * (x * pi / 180.0)) / 3.0
        ret += (320.0 * (x * pi / 180.0)) / 3.0
        return ret

    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * (abs(x))**0.5
        ret += (20.0 * (6.0 * (x * pi / 180.0)) + 20.0 * (6.0 * (y * pi / 180.0))) / 2.0
        ret += (20.0 * (x * pi / 180.0)) / 2.0
        ret += (40.0 * (x * pi / 180.0)) / 3.0
        ret += (150.0 * (x * pi / 180.0)) / 3.0
        ret += (300.0 * (x * pi / 180.0)) / 3.0
        return ret

    dLat = transform_lat(lon - 105.0, lat - 35.0)
    dLon = transform_lon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * pi
    magic = 1 - ee * (radLat ** 2)
    sqrtMagic = (magic)**0.5
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi)
    dLon = (dLon * 180.0) / (a / sqrtMagic * (radLat) * pi)
    mgLat = lat + dLat
    mgLon = lon + dLon
    return mgLat, mgLon

# ---------------------- 侧边栏导航 ----------------------
with st.sidebar:
    st.title("导航")
    st.subheader("功能页面")
    page = st.radio("", ["航线规划", "飞行监控"], label_visibility="collapsed")
    
    st.subheader("坐标系")
    coord_sys = st.radio("", ["GCJ-02(高德/百度)", "WGS-84"], label_visibility="collapsed")
    
    st.divider()
    st.subheader("系统状态")
    if 'a_set' not in st.session_state:
        st.session_state.a_set = False
    if 'b_set' not in st.session_state:
        st.session_state.b_set = False
    
    if st.session_state.a_set:
        st.success("A点已设")
    else:
        st.success("A点未设")
    if st.session_state.b_set:
        st.success("B点已设")
    else:
        st.success("B点未设")

# ---------------------- 航线规划页面 ----------------------
if page == "航线规划":
    st.title("航线规划（3D地图）")
    st.subheader("坐标信息")

    col_mid, col_right = st.columns([3, 1])

    with col_right:
        st.subheader("控制面板")
        latA = st.number_input("起点A纬度", value=32.232200, format="%.6f")
        lonA = st.number_input("起点A经度", value=118.749000, format="%.6f")
        latB = st.number_input("终点B纬度", value=32.234300, format="%.6f")
        lonB = st.number_input("终点B经度", value=118.749000, format="%.6f")
        height = st.slider("飞行高度(m)", 0, 100, 46)
        
        if st.button("设置A点"):
            st.session_state.a_set = True
        if st.button("设置B点"):
            st.session_state.b_set = True

    with col_mid:
        # 3D地图渲染
        if coord_sys == "GCJ-02(高德/百度)":
            a_lat, a_lon = wgs84_to_gcj02(latA, lonA)
            b_lat, b_lon = wgs84_to_gcj02(latB, lonB)
        else:
            a_lat, a_lon = latA, lonA
            b_lat, b_lon = latB, lonB

        view_state = pdk.ViewState(
            latitude=(a_lat + b_lat)/2,
            longitude=(a_lon + b_lon)/2,
            zoom=16,
            pitch=45,
            bearing=0
        )

        # 点标记层
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=[
                {"position": [a_lon, a_lat], "color": [255, 0, 0], "radius": 10, "name": "起点A"},
                {"position": [b_lon, b_lat], "color": [0, 255, 0], "radius": 10, "name": "终点B"},
            ],
            get_position="position",
            get_color="color",
            get_radius="radius",
            pickable=True,
        )

        # 航线层
        line_layer = pdk.Layer(
            "LineLayer",
            data=[{"path": [[a_lon, a_lat], [b_lon, b_lat]]}],
            get_path="path",
            get_color=[0, 0, 255],
            get_width=2,
        )

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/satellite-v9",
            initial_view_state=view_state,
            layers=[point_layer, line_layer],
            height=500,
            tooltip={"text": "{name}"},
        ))

# ---------------------- 飞行监控（心跳图）页面 ----------------------
else:
    st.title("飞行监控（心跳包）")
    
    # 实时数据显示
    col1, col2, col3, col4 = st.columns(4)
    hb_time = col1.empty()
    hb_lat = col2.empty()
    hb_lon = col3.empty()
    hb_height = col4.empty()
    
    col5, col6, col7, col8 = st.columns(4)
    hb_battery = col5.empty()
    hb_status = col6.empty()
    hb_speed = col7.empty()
    hb_dir = col8.empty()

    # 心跳图容器
    st.subheader("心跳数据趋势")
    chart_container = st.empty()

    # 初始化数据
    if 'heartbeat_data' not in st.session_state:
        st.session_state.heartbeat_data = []

    # 模拟心跳刷新
    while True:
        t = time.strftime("%H:%M:%S")
        lat = round(32.2322 + random.uniform(-0.0005, 0.0005), 6)
        lon = round(118.749 + random.uniform(-0.0005, 0.0005), 6)
        h = random.randint(40, 50)
        bat = random.randint(80, 100)
        speed = round(random.uniform(5, 15), 1)
        direction = random.randint(0, 360)

        # 更新数值显示
        hb_time.metric("时间", t)
        hb_lat.metric("纬度", f"{lat}")
        hb_lon.metric("经度", f"{lon}")
        hb_height.metric("高度", f"{h} m")
        hb_battery.metric("电量", f"{bat}%")
        hb_status.success("连接正常")
        hb_speed.metric("飞行速度", f"{speed} m/s")
        hb_dir.metric("航向", f"{direction}°")

        # 更新心跳图数据
        st.session_state.heartbeat_data.append({
            "time": t,
            "height": h,
            "battery": bat,
            "speed": speed
        })
        if len(st.session_state.heartbeat_data) > 20:
            st.session_state.heartbeat_data.pop(0)
        
        df = pd.DataFrame(st.session_state.heartbeat_data)
        chart_container.line_chart(df, x="time", y=["height", "battery", "speed"], use_container_width=True)

        time.sleep(1)
