from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QListWidget, QListWidgetItem, 
                             QLineEdit, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot
from ..widgets.video_player import VideoPlayer

import os
import sys
# Ensure we can import from root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from camera_storage import load_cameras, add_camera, save_cameras, delete_camera, update_camera

class CameraItem(QListWidgetItem):
    def __init__(self, camera_data):
        name = camera_data.get('name', 'Unnamed')
        path = camera_data.get('video_path', '')
        cid = camera_data.get('camera_id', 'Unknown')
        status = camera_data.get('status', 'offline')
        
        super().__init__(f"[{cid}] {name} | {path.split('/')[-1]}")
        self.camera_data = camera_data
        self.name = name
        self.path = path
        self.camera_id = cid

class CamerasView(QWidget):
    camera_selected = Signal(str) # Path to the video file

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(20)
        
        self.current_monitoring_path = None
        self.current_editing_id = None # Store ID if editing an existing cam
        
        # Left side: Camera Management Panel
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(350)
        self.left_panel.setStyleSheet("""
            QFrame { background-color: #1a1a1a; border-radius: 12px; padding: 10px; }
            QLabel { color: #aaa; font-weight: bold; margin-bottom: 5px; }
            QLineEdit { background-color: #2a2a2a; color: #fff; padding: 8px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #333; }
            QPushButton { background-color: #333; color: #fff; font-weight: bold; border-radius: 5px; padding: 8px; border: none; }
            QPushButton:hover { background-color: #444; }
            QPushButton#ActionBtn { background-color: #00cc88; color: #fff; }
            QPushButton#DeleteBtn { background-color: #cc0033; color: #fff; }
            QListWidget { background-color: #222; color: #e0e0e0; border: none; border-radius: 5px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #333; }
            QListWidget::item:selected { background-color: #333; color: #00ff88; }
        """)
        
        self.l_layout = QVBoxLayout(self.left_panel)
        
        # 1. New/Edit Form
        self.form_header = QLabel("ADD NEW CAMERA")
        self.form_header.setStyleSheet("color: #00cc88; font-size: 14px;")
        self.l_layout.addWidget(self.form_header)
        
        self.btn_reset = QPushButton("Clear / New Camera")
        self.btn_reset.setStyleSheet("background-color: #444; color: #eee; font-size: 10px; margin-bottom: 5px;")
        self.btn_reset.clicked.connect(self._reset_form)
        self.l_layout.addWidget(self.btn_reset)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Camera Name (e.g. Lobby Entrance)")
        self.l_layout.addWidget(self.input_name)
        
        self.btn_select_file = QPushButton("Select Video File")
        self.btn_select_file.clicked.connect(self._on_select_file)
        self.l_layout.addWidget(self.btn_select_file)
        
        self.selected_path_label = QLabel("No file selected")
        self.selected_path_label.setStyleSheet("font-size: 10px; color: #666; margin-bottom: 10px;")
        self.l_layout.addWidget(self.selected_path_label)
        
        self.btn_main_action = QPushButton("SAVE AS NEW CAMERA")
        self.btn_main_action.setObjectName("ActionBtn")
        self.btn_main_action.clicked.connect(self._on_main_action)
        self.l_layout.addWidget(self.btn_main_action)
        
        self.btn_delete = QPushButton("DELETE CAMERA")
        self.btn_delete.setObjectName("DeleteBtn")
        self.btn_delete.setVisible(False)
        self.btn_delete.clicked.connect(self._on_delete)
        self.l_layout.addWidget(self.btn_delete)
        
        self.l_layout.addSpacing(20)
        
        # 2. Camera List
        self.l_layout.addWidget(QLabel("YOUR CAMERAS"))
        self.cam_list = QListWidget()
        self.cam_list.itemClicked.connect(self._on_item_clicked)
        self.l_layout.addWidget(self.cam_list)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff5555; font-size: 10px;")
        self.l_layout.addWidget(self.error_label)
        
        # Right Side: Video Player Panel
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: #0d0d0d; border-radius: 12px;")
        self.r_layout = QVBoxLayout(self.right_panel)
        
        self.p_header = QLabel("SELECT A CAMERA TO START MONITORING")
        self.p_header.setStyleSheet("color: #00ffcc; font-size: 16px; font-weight: bold;")
        self.r_layout.addWidget(self.p_header)
        
        self.hint = QLabel("TIP: Select a camera to edit its details or draw a new ROI.")
        self.hint.setStyleSheet("color: #555; font-size: 11px; margin-bottom: 10px;")
        self.r_layout.addWidget(self.hint)
        
        self.player = VideoPlayer()
        self.player.roi_selected.connect(self._on_roi_drawn)
        self.r_layout.addWidget(self.player, stretch=1)
        
        # Layout Assembly
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.right_panel, stretch=1)
        
        self._load_saved_cameras()

    def _load_saved_cameras(self):
        self.cam_list.clear()
        cameras = load_cameras()
        for cam in cameras:
            item = CameraItem(cam)
            self.cam_list.addItem(item)
            
    def _reset_form(self):
        self.current_editing_id = None
        self.current_file_path = None
        self.input_name.clear()
        self.selected_path_label.setText("No file selected")
        self.form_header.setText("ADD NEW CAMERA")
        self.form_header.setStyleSheet("color: #00cc88;")
        self.btn_main_action.setText("SAVE AS NEW CAMERA")
        self.btn_delete.setVisible(False)
        self.error_label.setText("")

    def _on_select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Videos (*.mp4 *.avi *.mov *.mkv)")
        if file_path:
            self.current_file_path = file_path
            self.selected_path_label.setText(os.path.basename(file_path))

    def _on_main_action(self):
        name = self.input_name.text().strip()
        path = getattr(self, 'current_file_path', None)
        
        if not name or not path:
            self.error_label.setText("Error: Enter name and select file")
            return
            
        try:
            if self.current_editing_id:
                # UPDATE Mode
                update_camera(self.current_editing_id, {'name': name, 'video_path': path})
                self.error_label.setText("Updated successfully!")
            else:
                # ADD Mode
                add_camera({"name": name, "video_path": path})
                self.error_label.setText("Added successfully!")
            
            self._load_saved_cameras()
            self._reset_form()
            
        except Exception as e:
            self.error_label.setText(f"Error: {str(e)}")

    def _on_delete(self):
        if self.current_editing_id:
            delete_camera(self.current_editing_id)
            self._load_saved_cameras()
            self._reset_form()
            self.p_header.setText("CAMERA DELETED")
            self.current_monitoring_path = None

    def _on_item_clicked(self, item):
        # 1. Start Monitoring
        self.current_monitoring_path = item.path
        self.p_header.setText(f"MONITORING: {item.name.upper()}")
        self.camera_selected.emit(item.path)
        
        # 2. Enter EDIT Mode in form
        self.current_editing_id = item.camera_id
        self.current_file_path = item.path
        self.input_name.setText(item.name)
        self.selected_path_label.setText(os.path.basename(item.path))
        
        self.form_header.setText(f"EDITING: {item.camera_id}")
        self.form_header.setStyleSheet("color: #ffaa00;")
        self.btn_main_action.setText("SAVE CHANGES")
        self.btn_delete.setVisible(True)

    @Slot(int, int, int, int)
    def _on_roi_drawn(self, x, y, w, h):
        if not self.current_monitoring_path:
            return
            
        cameras = load_cameras()
        new_roi = (x, y, x + w, y + h)
        
        for cam in cameras:
            if cam['video_path'] == self.current_monitoring_path:
                cam['intrusion_roi'] = new_roi
                save_cameras(cameras)
                self.p_header.setText(f"New ROI Saved: {new_roi}")
                self.camera_selected.emit(self.current_monitoring_path)
                break
