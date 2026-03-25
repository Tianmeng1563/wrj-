import streamlit as st

# 页面设置
st.set_page_config(page_title="无人机智能化应用", layout="wide")

# 侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio("功能页面", ["航线规划", "飞行监控"])

# 坐标系选择
coord_type = st.sidebar.radio("坐标系", ["GCJ-02(高德/百度)", "WGS-84"], index=0)
st.sidebar.divider()

# 状态显示
st.sidebar.subheader("系统状态")
status_a = st.sidebar.empty()
status_b = st.sidebar.empty()

# 全局变量
if "point_a" not in st.session_state:
    st.session_state.point_a = None
if "point_b" not in st.session_state:
    st.session_state.point_b = None

# ---------------------- 航线规划页面 ----------------------
if page == "航线规划":
    st.title("航线规划")

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
        st.subheader("坐标信息")
        if st.session_state.point_a:
            st.success(f"起点A：{st.session_state.point_a}")
        if st.session_state.point_b:
            st.success(f"终点B：{st.session_state.point_b}")

    # 更新状态
    status_a.success("A点已设" if st.session_state.point_a else "A点未设")
    status_b.success("B点已设" if st.session_state.point_b else "B点未设")

# ---------------------- 飞行监控页面 ----------------------
elif page == "飞行监控":
    st.title("飞行监控（心跳包）")

    st.subheader("实时心跳包数据")
    st.write("设备状态：在线")
    st.write("信号强度：96%")
    st.write("电压：12.5V")
    st.write("飞行模式：正常")
    st.write("连接方式：WiFi")

    st.progress(96)
