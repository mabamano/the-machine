from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot
from ..widgets.video_player import VideoPlayer, StreamContainer
from ..widgets.alert_card import AlertCard

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(20)
        
        # 1. Stats Row
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(15)
        
        self.cameras_box = self._create_stat_box("Active Cameras", "0", "#00ffcc")
        self.alerts_box = self._create_stat_box("Alerts Today", "0", "#ff5555")
        self.people_box = self._create_stat_box("People Detected", "0", "#0088ff")
        
        self.stats_row.addWidget(self.cameras_box)
        self.stats_row.addWidget(self.alerts_box)
        self.stats_row.addWidget(self.people_box)
        self.layout.addLayout(self.stats_row)
        
        # 2. Main Content (Video + Recent Alerts)
        self.content_row = QHBoxLayout()
        self.content_row.setSpacing(20)
        
        # Video Container
        self.live_preview = StreamContainer("LIVE SYSTEM OVERVIEW")
        self.content_row.addWidget(self.live_preview, stretch=2)
        
        # Alerts Sidebar (Recent)
        self.alerts_sidebar = QVBoxLayout()
        self.alerts_title = QLabel("RECENT ALERTS")
        self.alerts_title.setStyleSheet("color: #ff5555; font-weight: bold; margin-bottom: 5px;")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        
        self.alerts_sidebar.addWidget(self.alerts_title)
        self.alerts_sidebar.addWidget(self.scroll_area)
        
        self.content_row.addLayout(self.alerts_sidebar, stretch=1)
        self.layout.addLayout(self.content_row, stretch=1)

    def _create_stat_box(self, label, value, color):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1a;
                border-radius: 12px;
                padding: 15px;
                border-bottom: 3px solid {color};
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setAlignment(Qt.AlignCenter)
        
        v_label = QLabel(value)
        v_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        
        l_label = QLabel(label)
        l_label.setStyleSheet("font-size: 14px; color: #777;")
        
        layout.addWidget(v_label, alignment=Qt.AlignCenter)
        layout.addWidget(l_label, alignment=Qt.AlignCenter)
        return box

    def add_alert(self, alert_type, message, severity="High"):
        card = AlertCard(alert_type, message, severity=severity)
        self.scroll_layout.insertWidget(0, card)
        
        # Update alert count (Simulated increment)
        current = int(self.alerts_box.findChildren(QLabel)[0].text())
        self.alerts_box.findChildren(QLabel)[0].setText(str(current + 1))

    def update_frame(self, frame):
        self.live_preview.player.update_frame(frame)
        
    def update_stats(self, cam_count, p_count):
        self.cameras_box.findChildren(QLabel)[0].setText(str(cam_count))
        self.people_box.findChildren(QLabel)[0].setText(str(p_count))

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = DashboardView()
    window.show()
    sys.exit(app.exec())
