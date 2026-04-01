from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, QDateTime, Signal

class AlertCard(QFrame):
    clicked = Signal(object) # Emits the snapshot frame

    def __init__(self, alert_type, message, camera_id="CAM_01", severity="High", parent=None, snapshot=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.snapshot_frame = snapshot
        
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
            QFrame:hover {{
                background-color: #252525;
            }}
            QLabel {{ border: none; background: transparent; color: #e0e0e0; }}
            #Type {{ font-weight: bold; color: {border_color}; font-size: 14px; }}
            #Time {{ color: #777; font-size: 11px; }}
        """)
        
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        info_layout = QVBoxLayout()
        
        # Ensure text is very bright white
        self.type_label = QLabel(alert_type.upper() if alert_type else "UNKNOWN")
        self.type_label.setObjectName("Type")
        self.type_label.setFixedHeight(20)
        
        self.msg_label = QLabel(f"{message}")
        self.msg_label.setWordWrap(True)
        self.msg_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 500;")
        
        self.time_label = QLabel(QDateTime.currentDateTime().toString("hh:mm:ss"))
        self.time_label.setObjectName("Time")
        self.time_label.setFixedWidth(60)
        
        info_layout.addWidget(self.type_label)
        info_layout.addWidget(self.msg_label)
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(self.time_label, alignment=Qt.AlignRight | Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.snapshot_frame)
            super().mousePressEvent(event)
