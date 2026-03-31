import sys
import json
import os
from PyQt5.QtCore import Qt, QUrl, pyqtSlot, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QFrame, QSizePolicy, QStatusBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from shapely.geometry import Polygon, Point
from shapely import wkt

# 全局变量：存储多边形坐标（记忆功能）
polygon_memory = None

class DroneMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("无人机智能化应用 - 分组作业4-项目Demo")
        self.setGeometry(100, 100, 1200, 800)

        # 1. 核心数据
        self.point_a = None  # (lat, lon)
        self.point_b = None
        self.init_ui()
        self.update_map()

    def init_ui(self):
        # 中心部件与主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- 左侧：控制面板 (30%宽度) ---
        control_frame = QFrame()
        control_frame.setMaximumWidth(400)
        control_layout = QVBoxLayout(control_frame)

        # A点设置
        control_layout.addWidget(QLabel("<b>A点设置 (GCJ-02)</b>"))
        self.a_lat_edit = QLineEdit("39.9042")
        self.a_lon_edit = QLineEdit("116.4074")
        control_layout.addWidget(QLabel("纬度:"))
        control_layout.addWidget(self.a_lat_edit)
        control_layout.addWidget(QLabel("经度:"))
        control_layout.addWidget(self.a_lon_edit)
        self.set_a_btn = QPushButton("设置A点")
        self.set_a_btn.clicked.connect(self.set_point_a)
        control_layout.addWidget(self.set_a_btn)

        # B点设置
        control_layout.addWidget(QLabel("<b>B点设置 (GCJ-02)</b>"))
        self.b_lat_edit = QLineEdit("39.9950")
        self.b_lon_edit = QLineEdit("116.3920")
        control_layout.addWidget(QLabel("纬度:"))
        control_layout.addWidget(self.b_lat_edit)
        control_layout.addWidget(QLabel("经度:"))
        control_layout.addWidget(self.b_lon_edit)
        self.set_b_btn = QPushButton("设置B点")
        self.set_b_btn.clicked.connect(self.set_point_b)
        control_layout.addWidget(self.set_b_btn)

        # 多边形圈选功能
        control_layout.addWidget(QLabel("<b>障碍圈选</b>"))
        self.polygon_info_label = QLabel("当前圈选状态: 未圈选")
        control_layout.addWidget(self.polygon_info_label)
        
        # 圈选按钮
        self.start_draw_btn = QPushButton("开始圈选障碍")
        self.start_draw_btn.clicked.connect(self.enter_draw_mode)
        control_layout.addWidget(self.start_draw_btn)
        
        self.clear_polygon_btn = QPushButton("清除圈选")
        self.clear_polygon_btn.clicked.connect(self.clear_polygon)
        control_layout.addWidget(self.clear_polygon_btn)

        # 状态显示
        control_layout.addStretch()
        self.status_label = QLabel("系统状态: 已连接")
        control_layout.addWidget(self.status_label)

        # --- 右侧：地图显示区 (70%宽度) ---
        self.web_view = QWebEngineView()
        main_layout.addWidget(control_frame, 1)
        main_layout.addWidget(self.web_view, 4)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def gcj02_to_wgs84(self, lat, lon):
        """
        简易GCJ-02(火星坐标系)转WGS84示例
        作业演示用，实际项目需引入专业库
        """
        # 此处为简化示例，实际转换逻辑略复杂，这里直接返回原坐标
        # 你可以根据作业要求补充完整转换算法
        return lat, lon

    @pyqtSlot()
    def set_point_a(self):
        try:
            lat = float(self.a_lat_edit.text())
            lon = float(self.a_lon_edit.text())
            # 坐标转换演示
            wgs_lat, wgs_lon = self.gcj02_to_wgs84(lat, lon)
            self.point_a = (wgs_lat, wgs_lon)
            self.status_bar.showMessage(f"A点已设置: GCJ-02({lat}, {lon}) -> WGS84({wgs_lat}, {wgs_lon})")
            self.update_map()
        except ValueError:
            self.status_bar.showMessage("A点坐标输入错误!", 2000)

    @pyqtSlot()
    def set_point_b(self):
        try:
            lat = float(self.b_lat_edit.text())
            lon = float(self.b_lon_edit.text())
            wgs_lat, wgs_lon = self.gcj02_to_wgs84(lat, lon)
            self.point_b = (wgs_lat, wgs_lon)
            self.status_bar.showMessage(f"B点已设置: GCJ-02({lat}, {lon}) -> WGS84({wgs_lat}, {wgs_lon})")
            self.update_map()
        except ValueError:
            self.status_bar.showMessage("B点坐标输入错误!", 2000)

    @pyqtSlot()
    def enter_draw_mode(self):
        """进入地图绘制模式，通过JS交互获取多边形"""
        self.status_bar.showMessage("请在地图上绘制多边形（点击添加顶点，右键结束）")
        # 注入JS交互逻辑，通知网页端开启绘制模式
        self.web_view.page().runJavaScript("enableDrawMode(true)")

    @pyqtSlot()
    def clear_polygon(self):
        """清除多边形圈选"""
        global polygon_memory
        polygon_memory = None
        self.polygon_info_label.setText("当前圈选状态: 已清除")
        self.status_bar.showMessage("多边形已清除")
        self.update_map()

    @pyqtSlot(str)
    def receive_polygon(self, polygon_wkt):
        """
        接收从JS传来的多边形数据 (WKT格式)
        实现记忆功能：保存到全局变量
        """
        global polygon_memory
        try:
            # 解析WKT，验证有效性
            poly = wkt.loads(polygon_wkt)
            if isinstance(poly, Polygon):
                polygon_memory = polygon_wkt  # 记忆功能
                self.polygon_info_label.setText(f"当前圈选状态: 已保存 {len(poly.exterior.coords)} 个顶点")
                self.status_bar.showMessage("多边形圈选成功，已记忆！")
                self.update_map()
            else:
                self.status_bar.showMessage("绘制的不是有效多边形!", 2000)
        except Exception as e:
            self.status_bar.showMessage(f"解析失败: {str(e)}", 3000)

    def update_map(self):
        """
        生成Folium地图HTML，包含实时更新逻辑
        """
        import folium
        
        # 地图中心默认取A点或B点
        if self.point_a:
            m = folium.Map(location=self.point_a, zoom_start=12, tiles="OpenStreetMap")
        elif self.point_b:
            m = folium.Map(location=self.point_b, zoom_start=12, tiles="OpenStreetMap")
        else:
            m = folium.Map(location=(39.9042, 116.4074), zoom_start=12, tiles="OpenStreetMap")

        # 1. 绘制A/B点
        if self.point_a:
            folium.CircleMarker(
                location=self.point_a,
                radius=8,
                color="red",
                fill=True,
                fill_color="red",
                popup="A点",
                tooltip="A点"
            ).add_to(m)
        
        if self.point_b:
            folium.CircleMarker(
                location=self.point_b,
                radius=8,
                color="green",
                fill=True,
                fill_color="green",
                popup="B点",
                tooltip="B点"
            ).add_to(m)

        # 2. 绘制连线
        if self.point_a and self.point_b:
            folium.PolyLine(
                locations=[self.point_a, self.point_b],
                color="blue",
                weight=3,
                opacity=0.7
            ).add_to(m)

        # 3. 绘制记忆中的多边形 (障碍圈选)
        global polygon_memory
        if polygon_memory:
            try:
                poly = wkt.loads(polygon_memory)
                folium.GeoJson(
                    data={
                        "type": "Polygon",
                        "coordinates": [list(poly.exterior.coords)]
                    },
                    name="障碍区域",
                    style_function=lambda x: {
                        "fillColor": "#ff0000",
                        "color": "#ff0000",
                        "weight": 2,
                        "fillOpacity": 0.2
                    }
                ).add_to(m)
            except Exception as e:
                print(f"绘制多边形失败: {e}")

        # 4. 注入自定义JS (实现圈选交互与实时更新)
        map_html = m.get_root().render()
        
        custom_js = """
        <script>
        let drawMode = false;
        let polygonPoints = [];
        let polygonLayer = null;

        // 监听Python端的绘制模式切换
        function enableDrawMode(enable) {
            drawMode = enable;
            if (enable) {
                alert("请在地图上点击绘制多边形，右键点击结束。");
            }
        }

        // 地图点击事件
        map.on('click', function(e) {
            if (drawMode) {
                const lat = e.latlng.lat;
                const lng = e.latlng.lng;
                polygonPoints.push([lat, lng]);
                
                // 临时绘制
                if (polygonLayer) {
                    map.removeLayer(polygonLayer);
                }
                polygonLayer = L.polygon(polygonPoints, {color: 'blue', fillOpacity: 0.2}).addTo(map);
            }
        });

        // 地图右键结束绘制
        map.on('contextmenu', function(e) {
            if (drawMode && polygonPoints.length > 2) {
                // 转换为WKT格式发送给Python
                const wkt = 'POLYGON((' + polygonPoints.map(p => p[1] + ' ' + p[0]).join(',') + '))';
                window.pyqtBridge.receivePolygon(wkt); // 调用Qt信号
                
                // 重置状态
                drawMode = false;
                polygonPoints = [];
            } else if (drawMode) {
                alert("多边形至少需要3个顶点!");
            }
        });

        // 暴露接口给Qt
        window.pyqtBridge = {
            receivePolygon: function(wkt) {
                // 此函数会被Qt的receive_polygon槽函数接管
                // 实际通信通过QWebChannel实现，此处为示意
                console.log("发送多边形数据:", wkt);
                // 真实项目中需使用 QWebChannel 连接
            }
        };
        </script>
        """

        # 合并HTML
        final_html = map_html.replace("</body>", f"{custom_js}</body>")
        self.web_view.setHtml(final_html)

        # 5. 模拟心跳与实时更新 (演示实时性)
        # 实际项目中可替换为传感器数据回调
        QTimer.singleShot(2000, self.simulate_heartbeat)

    def simulate_heartbeat(self):
        """模拟心跳数据更新，演示实时性"""
        # 此处可替换为实际的串口/网络数据接收逻辑
        self.status_bar.showMessage("📶 心跳正常 | 地图数据已实时更新")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DroneMapApp()
    window.show()
    sys.exit(app.exec_())sleep(1)
