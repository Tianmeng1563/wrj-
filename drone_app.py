import streamlit as st
import pydeck as pdk

st.set_page_config(page_title="无人机智能化应用", layout="wide")

# 侧边栏
st.sidebar.title("导航")
page = st.sidebar.radio("功能页面", ["航线规划", "飞行监控"])

coord_type = st.sidebar.radio("坐标系", ["GCJ-02(高德/百度)", "WGS-84"], index=0)
st.sidebar.divider()

st.sidebar.subheader("系统状态")
status_a = st.sidebar.empty()
status_b = st.sidebar.empty()

if "point_a" not in st.session_state:
    st.session_state.point_a = None
if "point_b" not in st.session_state:
    st.session_state.point_b = None

# 航线规划（带3D地图）
if page == "航线规划":
    st.title("航线规划（3D地图）")
    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("控制面板")
        lat_a = st.number_input("起点A 纬度", value=32.2322, format="%.6f")
        lng_a = st.number_input("起点A 经度", value=118.7490, format="%.6f")
        lat_b = st.number_input("终点B 纬度", value=32.2343, format="%.6f")
        lng_b = st.number_input("终点B 经度", value=118.7490, format="%.6f")
        height = st.slider("飞行高度(m)", 10, 120, 50)

        if st.button("设置A点"):
            st.session_state.point_a = (lat_a, lng_a)
        if st.button("设置B点"):
            st.session_state.point_b = (lat_b, lng_b)

    with col1:
        # 3D地图
        view_state = pdk.ViewState(
            latitude=32.233,
            longitude=118.749,
            zoom=16,
            pitch=45,
        )
        layers = []
        if st.session_state.point_a:
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=[{"position": [st.session_state.point_a[1], st.session_state.point_a[0]]}],
                get_position="position",
                get_radius=15,
                get_color=[255, 0, 0],
            ))
        if st.session_state.point_b:
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=[{"position": [st.session_state.point_b[1], st.session_state.point_b[0]]}],
                get_position="position",
                get_radius=15,
                get_color=[0, 255, 0],
            ))

        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=view_state,
            layers=layers,
            height=500,
        ))

    status_a.success("A点已设" if st.session_state.point_a else "A点未设")
    status_b.success("B点已设" if st.session_state.point_b else "B点未设")

# 飞行监控（心跳包）
elif page == "飞行监控":
    st.title("飞行监控（心跳包）")
    st.subheader("实时心跳包数据")
    st.write("设备状态：在线")
    st.write("信号强度：96%")
    st.write("电压：12.5V")
    st.write("飞行模式：正常")
    st.write("连接方式：WiFi")
    st.write("GPS 状态：已锁定")
    st.write("电池剩余：85%")
    st.progress(96)
