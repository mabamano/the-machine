from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QLabel, QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from .sidebar import Sidebar
from .views.dashboard_view import DashboardView
from .views.cameras_view import CamerasView
from .views.find_view import FindView
from .views.anomalies_view import AnomaliesView

class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Smart Surveillance Dashboard")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #0d0d0d; color: #fff; font-family: 'Outfit', sans-serif;")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Sidebar
        self.sidebar = Sidebar()
        self.sidebar.nav_changed.connect(self._switch_view)
        self.sidebar.btn_logout.clicked.connect(self.logout_requested.emit)
        self.main_layout.addWidget(self.sidebar)
        
        # 2. Main Content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Top Bar
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(60)
        self.top_bar.setStyleSheet("background-color: #0d0d0d; border-bottom: 1px solid #222; padding: 0 20px;")
        t_l = QHBoxLayout(self.top_bar)
        
        self.title_label = QLabel("MOCK FEED ACTIVE: DASHBOARD OVERVIEW")
        self.title_label.setStyleSheet("color: #777; font-weight: bold; font-size: 14px;")
        t_l.addWidget(self.title_label)
        
        t_l.addStretch(1)
        
        # User Info
        self.user_label = QLabel("ADMINISTRATOR")
        self.user_label.setStyleSheet("color: #888; margin-right: 15px;")
        t_l.addWidget(self.user_label)
        
        self.content_layout.addWidget(self.top_bar)
        
        # Stacked Views
        self.stack = QStackedWidget()
        self.view_dashboard = DashboardView()
        self.view_cameras = CamerasView()
        self.view_find = FindView()
        self.view_anomalies = AnomaliesView()
        
        self.stack.addWidget(self.view_dashboard)
        self.stack.addWidget(self.view_cameras)
        self.stack.addWidget(self.view_find)
        self.stack.addWidget(self.view_anomalies)
        
        self.content_layout.addWidget(self.stack)
        
        self.main_layout.addWidget(self.content_widget, stretch=1)

    def _switch_view(self, index):
        self.stack.setCurrentIndex(index)
        # Update title based on view
        titles = ["DASHBOARD OVERVIEW", "CAMERA MANAGEMENT", "PERSON SEARCH", "ANOMALY MONITORING"]
        self.title_label.setText(f"MOCK FEED ACTIVE | {titles[index]}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
