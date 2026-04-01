from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QFrame, QGridLayout, 
                             QProgressBar, QScrollArea, QSizePolicy)
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PySide6.QtCore import Qt, Signal, Slot, QTimer
import cv2
import numpy as np

class FindView(QWidget):
    search_triggered = Signal(str) # Path to the search image
    search_completed = Signal(dict) # Results from the backend

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
        
        self.search_completed.connect(self._show_mock_results)
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
            self._run_search() # Start search instantly

    def _run_search(self):
        # Notify the rest of the system about the new target
        self.search_triggered.emit(self.current_img_path)
        
        # Display progress or message (Results will come via signal)
        self.grid_layout.addWidget(QLabel("Searching..."), 0, 0)

    def _update_progress(self):
        val = self.progress.value() + 5
        self.progress.setValue(val)
        if val >= 100:
            self.timer.stop()
            self.progress.setVisible(False)
            self.btn_search.setEnabled(True)
            self._show_mock_results()

    def _show_mock_results(self, result):
        # Clear previous results first
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)

        if result["status"] == "no_match":
            no_match = QLabel("NO MATCH FOUND")
            no_match.setStyleSheet("color: #ff4444; font-size: 18px; font-weight: bold;")
            no_match.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(no_match, 0, 0, 1, 2)
            return

        # Create localized result item for match
        res_item = QFrame()
        res_item.setFixedSize(300, 150)
        res_item.setStyleSheet("background-color: #002244; border: 2px solid #0088ff; border-radius: 12px;")
        
        l = QVBoxLayout(res_item)
        l.setContentsMargins(15, 15, 15, 15)
        
        match_title = QLabel("MATCH DETECTED: ACTIVE DATABASE")
        match_title.setStyleSheet("color: #00ffff; font-weight: bold; font-size: 14px;")
        l.addWidget(match_title)
        
        name_info = QLabel(f"<span style='color: #fff; font-size: 20px;'>{result['name']}</span>")
        conf_info = QLabel(f"<span style='color: #00ffcc;'>Confidence: {result['confidence']*100:.1f}%</span>")
        source_info = QLabel(f"<span style='color: #888;'>Source: Active Surveillance Feed</span>")
        
        l.addWidget(name_info)
        l.addWidget(conf_info)
        l.addWidget(source_info)
        
        self.grid_layout.addWidget(res_item, 0, 0, 1, 2)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = FindView()
    window.show()
    sys.exit(app.exec())
