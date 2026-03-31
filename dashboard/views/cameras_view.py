from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem, 
                             QLineEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from ..widgets.video_player import VideoPlayer

class CameraItem(QListWidgetItem):
    def __init__(self, name, path):
        super().__init__(f"🎥 {name} - {path.split('/')[-1]}")
        self.name = name
        self.path = path
        self.status = "Active"

class CamerasView(QWidget):
    camera_selected = Signal(str) # Path to the video file

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(20)
        
        # Left side: Camera List & Add Form
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(300)
        self.left_panel.setStyleSheet("""
            QFrame { background-color: #1a1a1a; border-radius: 12px; padding: 10px; }
            QLabel { color: #aaa; font-weight: bold; margin-bottom: 5px; }
            QLineEdit { background-color: #2a2a2a; color: #fff; padding: 8px; border-radius: 5px; margin-bottom: 10px; }
            QPushButton#AddBtn { background-color: #00cc88; color: #fff; font-weight: bold; border-radius: 5px; padding: 10px; }
            QListWidget { background-color: #222; color: #e0e0e0; border: none; border-radius: 5px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #333; }
        """)
        
        self.l_layout = QVBoxLayout(self.left_panel)
        
        # Header
        self.header = QLabel("MANAGE CAMERAS")
        self.l_layout.addWidget(self.header)
        
        # Form
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Camera Name (e.g. Lobby Entrance)")
        self.l_layout.addWidget(self.input_name)
        
        self.btn_select_file = QPushButton("Select Video File")
        self.btn_select_file.setStyleSheet("background-color: #333; color: #ccc;")
        self.btn_select_file.clicked.connect(self._on_select_file)
        self.l_layout.addWidget(self.btn_select_file)
        
        self.selected_path = QLabel("No file selected")
        self.selected_path.setStyleSheet("font-size: 10px; color: #666; margin-bottom: 10px;")
        self.l_layout.addWidget(self.selected_path)
        
        self.btn_add = QPushButton("ADD CAMERA")
        self.btn_add.setObjectName("AddBtn")
        self.btn_add.clicked.connect(self._add_camera)
        self.l_layout.addWidget(self.btn_add)
        
        self.l_layout.addSpacing(20)
        
        # List
        self.cam_list = QListWidget()
        self.cam_list.itemClicked.connect(self._on_item_clicked)
        self.l_layout.addWidget(self.cam_list)
        
        self.layout.addWidget(self.left_panel)
        
        # Right side: Large Preview area
        self.preview_panel = QFrame()
        self.preview_panel.setStyleSheet("background-color: #0d0d0d; border-radius: 12px;")
        self.p_layout = QVBoxLayout(self.preview_panel)
        
        self.preview_header = QLabel("CAMERA MONITOR")
        self.preview_header.setStyleSheet("color: #00ffcc; font-size: 18px; font-weight: bold;")
        self.p_layout.addWidget(self.preview_header)
        
        self.player = VideoPlayer()
        self.p_layout.addWidget(self.player, stretch=1)
        
        self.layout.addWidget(self.preview_panel, stretch=1)

    def _on_select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.mp4 *.avi *.mov *.mkv)")
        if file_path:
            self.current_file_path = file_path
            self.selected_path.setText(file_path.split("/")[-1])

    def _add_camera(self):
        name = self.input_name.text().strip()
        if not name or not hasattr(self, 'current_file_path'):
            return
            
        item = CameraItem(name, self.current_file_path)
        self.cam_list.addItem(item)
        
        # Clear inputs
        self.input_name.clear()
        self.selected_path.setText("No file selected")
        del self.current_file_path

    def _on_item_clicked(self, item):
        self.preview_header.setText(f"MONITORING: {item.name.upper()}")
        self.camera_selected.emit(item.path)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = CamerasView()
    window.show()
    sys.exit(app.exec())
