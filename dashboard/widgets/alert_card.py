from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QDateTime

class AlertCard(QFrame):
    def __init__(self, alert_type, message, camera_id="CAM_01", severity="High", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Style based on severity
        border_color = "#ff5555" if severity == "High" else "#ffaa00" if severity == "Medium" else "#00ff00"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1a;
                border-left: 5px solid {border_color};
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 5px;
            }}
            QLabel {{ border: none; background: transparent; color: #e0e0e0; }}
            #Type {{ font-weight: bold; color: {border_color}; font-size: 14px; }}
            #Time {{ color: #777; font-size: 11px; }}
        """)
        
        layout = QHBoxLayout(self)
        info_layout = QVBoxLayout()
        
        self.type_label = QLabel(alert_type.upper())
        self.type_label.setObjectName("Type")
        
        self.msg_label = QLabel(f"<b>{message}</b> | ID: {camera_id}")
        self.msg_label.setStyleSheet("color: #ccc; font-size: 13px;")
        
        self.time_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
        self.time_label.setObjectName("Time")
        
        info_layout.addWidget(self.type_label)
        info_layout.addWidget(self.msg_label)
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(self.time_label, alignment=Qt.AlignRight | Qt.AlignTop)
