from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, Signal, Slot
import cv2

class VideoPlayer(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(480, 360)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QLabel {
                background-color: #121212; 
                border: 2px solid #333; 
                border-radius: 12px;
                color: #555;
                font-family: 'Outfit', sans-serif;
                font-size: 18px;
            }
        """)
        self.setText("🎥 NO FEED DETECTED")
        self.setScaledContents(True)

    @Slot(object)
    def update_frame(self, frame):
        """
        Updates the player with a new OpenCV frame.
        """
        if frame is None:
            return
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.setPixmap(QPixmap.fromImage(qt_img))

class StreamContainer(QFrame):
    """
    A stylized container for the video player with header.
    """
    def __init__(self, title="CAMERA STREAM", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #00ffcc; font-weight: bold; margin-bottom: 5px;")
        
        self.player = VideoPlayer()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.player)
