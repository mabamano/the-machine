from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QIcon

class SidebarButton(QPushButton):
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self.setText(f"  {text}")
        # icon_text for simple text-based icons or placeholder
        self.setFixedHeight(50)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton { 
                background-color: transparent; border: none; text-align: left; 
                padding-left: 20px; font-size: 15px; color: #888; 
                border-radius: 8px; margin: 2px 10px;
            }
            QPushButton:hover { background-color: #1a1a1a; color: #ccc; }
            QPushButton:checked { background-color: #00ffcc; color: #000; font-weight: bold; }
        """)

class Sidebar(QWidget):
    nav_changed = Signal(int) # Index of the screen

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setStyleSheet("background-color: #0d0d0d; border-right: 1px solid #222;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 20, 0, 20)
        self.layout.setSpacing(5)
        
        # Logo Area
        self.logo = QLabel("🛡️ SURVEILLANCE")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("color: #00ffcc; font-size: 20px; font-weight: bold; margin-bottom: 30px;")
        self.layout.addWidget(self.logo)
        
        # Navigation Buttons
        self.buttons = []
        self.btn_dashboard = SidebarButton("Dashboard", "📊")
        self.btn_cameras = SidebarButton("Cameras", "📷")
        self.btn_find = SidebarButton("Find Someone", "🔍")
        self.btn_anomalies = SidebarButton("Anomalies", "⚠️")
        
        self.buttons.extend([self.btn_dashboard, self.btn_cameras, self.btn_find, self.btn_anomalies])
        
        for i, btn in enumerate(self.buttons):
            self.layout.addWidget(btn)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_btn_clicked(idx))
            
        self.layout.addStretch(1)
        
        # Logout footer
        self.btn_logout = QPushButton("🚪 Logout")
        self.btn_logout.setStyleSheet("""
            QPushButton { 
                background-color: transparent; color: #777; border-top: 1px solid #222; 
                padding: 20px; text-align: left; 
            }
            QPushButton:hover { color: #ff5555; }
        """)
        self.layout.addWidget(self.btn_logout)
        
        # Set default
        self._on_btn_clicked(0)

    def _on_btn_clicked(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.nav_changed.emit(index)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = Sidebar()
    window.show()
    sys.exit(app.exec())
