from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QFrame, QGridLayout, 
                             QProgressBar, QScrollArea, QSizePolicy)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PySide6.QtCore import Qt, Signal, Slot, QTimer
import cv2
import numpy as np

class FindView(QWidget):
    search_triggered = Signal(str) # Path to the search image

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # Header
        self.header = QLabel("PERSON SEARCH")
        self.header.setStyleSheet("color: #0088ff; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header)
        
        # Main Area
        self.main_row = QHBoxLayout()
        self.main_row.setSpacing(20)
        
        # Left Panel: Search Query
        self.query_panel = QFrame()
        self.query_panel.setFixedWidth(350)
        self.query_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; padding: 15px;")
        self.q_layout = QVBoxLayout(self.query_panel)
        self.q_layout.setAlignment(Qt.AlignTop)
        
        self.q_title = QLabel("UPLOAD SEARCH IMAGE")
        self.q_title.setStyleSheet("color: #aaa; font-weight: bold; margin-bottom: 5px;")
        self.q_layout.addWidget(self.q_title)
        
        self.img_preview = QLabel("IMAGE PREVIEW")
        self.img_preview.setAlignment(Qt.AlignCenter)
        self.img_preview.setFixedSize(300, 300)
        self.img_preview.setStyleSheet("background-color: #121212; border: 2px dashed #444; border-radius: 8px; color: #555;")
        self.q_layout.addWidget(self.img_preview)
        
        self.btn_select = QPushButton("SELECT IMAGE")
        self.btn_select.setStyleSheet("background-color: #333; color: #fff; padding: 10px; border-radius: 5px;")
        self.btn_select.clicked.connect(self._on_select_image)
        self.q_layout.addWidget(self.btn_select)
        
        self.btn_search = QPushButton("SEARCH ACROSS FEEDS")
        self.btn_search.setStyleSheet("background-color: #0088ff; color: #fff; font-weight: bold; padding: 12px; border-radius: 5px; margin-top: 5px;")
        self.btn_search.clicked.connect(self._run_search)
        self.btn_search.setEnabled(False)
        self.q_layout.addWidget(self.btn_search)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar { background-color: #222; border-radius: 5px; text-align: center; color: #fff;}
            QProgressBar::chunk { background-color: #0088ff; border-radius: 5px; }
        """)
        self.progress.setVisible(False)
        self.q_layout.addWidget(self.progress)
        
        self.main_row.addWidget(self.query_panel)
        
        # Right Panel: Results
        self.res_panel = QFrame()
        self.res_panel.setStyleSheet("background-color: #1a1a1a; border-radius: 12px; padding: 15px;")
        self.r_layout = QVBoxLayout(self.res_panel)
        self.r_layout.setAlignment(Qt.AlignTop)
        
        self.r_title = QLabel("SEARCH RESULTS")
        self.r_title.setStyleSheet("color: #aaa; font-weight: bold; margin-bottom: 5px;")
        self.r_layout.addWidget(self.r_title)
        
        # Mock results list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.r_layout.addWidget(self.scroll)
        
        self.main_row.addWidget(self.res_panel)
        self.layout.addLayout(self.main_row, stretch=1)

    def _on_select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.current_img_path = file_path
            pix = QPixmap(file_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_preview.setPixmap(pix)
            self.btn_search.setEnabled(True)

    def _run_search(self):
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.btn_search.setEnabled(False)
        
        # Simulate search
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(50)
        
        # Clear previous results
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

    def _update_progress(self):
        val = self.progress.value() + 5
        self.progress.setValue(val)
        if val >= 100:
            self.timer.stop()
            self.progress.setVisible(False)
            self.btn_search.setEnabled(True)
            self._show_mock_results()

    def _show_mock_results(self):
        # Create dummy result items
        for i in range(4):
            res_item = QFrame()
            res_item.setFixedSize(150, 180)
            res_item.setStyleSheet("background-color: #222; border: 1px solid #333; border-radius: 8px;")
            l = QVBoxLayout(res_item)
            
            img = QLabel()
            img.setPixmap(QPixmap(self.current_img_path).scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            img.setAlignment(Qt.AlignCenter)
            
            info = QLabel(f"<b>CAM_0{i+1}</b><br><span style='color: #00ffcc;'>Match: 9{i}.2%</span>")
            info.setStyleSheet("color: #ccc; font-size: 11px;")
            info.setAlignment(Qt.AlignCenter)
            
            l.addWidget(img)
            l.addWidget(info)
            self.grid_layout.addWidget(res_item, i // 2, i % 2)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = FindView()
    window.show()
    sys.exit(app.exec())
