from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QComboBox, 
                             QSizePolicy, QSplitter)
from PySide6.QtCore import Qt, Signal, Slot
from ..widgets.alert_card import AlertCard

class AnomaliesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header Row
        h_row = QHBoxLayout()
        self.header = QLabel("ANOMALY MONITORING")
        self.header.setStyleSheet("color: #ff5555; font-size: 24px; font-weight: bold;")
        h_row.addWidget(self.header)
        
        # Filter dropdown
        self.filter = QComboBox()
        self.filter.addItems(["All Types", "Loitering", "Zone Violation", "Intrusion", "Running", "Fighting", "Fell Down"])
        self.filter.setStyleSheet("""
            QComboBox { background-color: #333; color: #fff; padding: 10px; border-radius: 5px; min-width: 150px; }
            QComboBox QAbstractItemView { background-color: #333; color: #fff; }
        """)
        h_row.addWidget(self.filter, alignment=Qt.AlignRight)
        self.layout.addLayout(h_row)
        
        # Main Splitter: Alert List | Snapshot Preview
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Alert List Panel
        self.list_panel = QFrame()
        self.list_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; padding: 10px;")
        self.l_l = QVBoxLayout(self.list_panel)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.alert_list_layout = QVBoxLayout(self.scroll_content)
        self.alert_list_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.l_l.addWidget(self.scroll)
        
        self.splitter.addWidget(self.list_panel)
        
        # Snapshot Panel
        self.snap_panel = QFrame()
        self.snap_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; padding: 15px;")
        self.s_l = QVBoxLayout(self.snap_panel)
        self.s_l.setAlignment(Qt.AlignCenter)
        
        self.snap_title = QLabel("SNAPSHOT PREVIEW")
        self.snap_title.setStyleSheet("color: #777; font-weight: bold; margin-bottom: 20px;")
        self.s_l.addWidget(self.snap_title)
        
        self.snap_img = QLabel("Select an alert to view snapshot")
        self.snap_img.setAlignment(Qt.AlignCenter)
        self.snap_img.setFixedSize(500, 350)
        self.snap_img.setStyleSheet("background-color: #0d0d0d; border: 2px solid #333; border-radius: 10px; color: #555;")
        self.s_l.addWidget(self.snap_img, stretch=1)
        
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        self.splitter.addWidget(self.snap_panel)
        
        self.layout.addWidget(self.splitter)

    @Slot(str, str, str, object)
    def add_anomaly_alert(self, alert_type, message, severity="High", snapshot=None):
        card = AlertCard(alert_type, message, severity=severity, snapshot=snapshot)
        card.clicked.connect(self._show_snapshot)
        self.alert_list_layout.insertWidget(0, card)
        
        # Limit history to 50
        if self.alert_list_layout.count() > 50:
            last = self.alert_list_layout.takeAt(self.alert_list_layout.count() - 1)
            if last.widget():
                last.widget().deleteLater()

    @Slot(object)
    def _show_snapshot(self, frame):
        if frame is None:
            self.snap_img.setText("No snapshot available for this alert")
            return
            
        import cv2
        from PySide6.QtGui import QImage, QPixmap
        
        # Process preview image
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # Scale to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.snap_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.snap_img.setPixmap(scaled_pixmap)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = AnomaliesView()
    window.show()
    sys.exit(app.exec())
