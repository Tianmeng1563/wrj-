import streamlit as st
import pydeck as pdk
import time
import random

# 深色主题
st.set_page_config(page_title="无人机Demo", layout="wide")

# 坐标系转换
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

# 页面
tab1, tab2 = st.tabs(["航线规划（3D地图）", "飞行监控（心跳包）"])

# 航线规划
with tab1:
    st.subheader("航线规划（3D地图）")
    st.write("坐标信息")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.success("起点A：(32.2322, 118.7490)")
        st.success("终点B：(32.6, 118.7490)")

    with col_right:
        st.subheader("控制面板")
        latA = st.number_input("起点A纬度", value=32.2322)
        lonA = st.number_input("起点A经度", value=118.7490)
        latB = st.number_input("终点B纬度", value=32.6)
        lonB = st.number_input("终点B经度", value=118.7490)
        height = st.slider("飞行高度(m)", 0, 100, 50)
        st.button("设置A点")
        st.button("设置B点")

    # 3D地图（必显示）
    a_lat, a_lon = wgs84_to_gcj02(latA, lonA)
    b_lat, b_lon = wgs84_to_gcj02(latB, lonB)

    view_state = pdk.ViewState(
        latitude=a_lat,
        longitude=a_lon,
        zoom=14,
        pitch=45,
        bearing=0
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[
            {"position": [a_lon, a_lat], "color": [255, 0, 0], "radius": 100},
            {"position": [b_lon, b_lat], "color": [0, 255, 0], "radius": 100},
        ],
        get_position="position",
        get_color="color",
        get_radius="radius",
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-v9",
        initial_view_state=view_state,
        layers=[layer],
        height=500
    ))

# 心跳监控
with tab2:
    st.subheader("飞行监控（心跳包）")
    hb_time = st.empty()
    hb_latlon = st.empty()
    hb_height = st.empty()
    hb_battery = st.empty()
    hb_status = st.empty()

    while True:
        t = time.strftime("%H:%M:%S")
        lat = round(32.2322 + random.uniform(-0.0005, 0.0005), 4)
        lon = round(118.749 + random.uniform(-0.0005, 0.0005), 4)
        h = random.randint(45, 55)
        bat = random.randint(80, 100)

        hb_time.metric("时间", t)
        hb_latlon.metric("坐标", f"{lat}, {lon}")
        hb_height.metric("高度", f"{h} m")
        hb_battery.metric("电量", f"{bat}%")
        hb_status.success("连接正常")

        time.sleep(1)
