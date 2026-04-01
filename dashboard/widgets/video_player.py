from PySide6.QtWidgets import QLabel, QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PySide6.QtCore import Qt, Signal, Slot, QPoint, QRect
import cv2

class VideoPlayer(QLabel):
    roi_selected = Signal(int, int, int, int) # x, y, w, h

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
        self.setText("NO SOURCE DETECTED")
        self.setScaledContents(True)
        
        # ROI Drawing State
        self.drawing = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_frame = None

    @Slot(object)
    def update_frame(self, frame):
        if frame is None: return
        self.current_frame = frame.copy()
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        
        # If currently drawing, draw the rect on the pixmap
        if self.drawing:
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor(255, 0, 0), 3, Qt.DashLine))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
            painter.end()
            
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.end_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.end_point = event.pos()
            
            # Normalize and Emit ROI
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.start_point.x() - self.end_point.x())
            h = abs(self.start_point.y() - self.end_point.y())
            
            # Since the QLabel is setScaledContents(True), 
            # the coordinates need to be mapped to the original image size
            if self.current_frame is not None:
                img_h, img_w = self.current_frame.shape[:2]
                real_x = int(x * img_w / self.width())
                real_y = int(y * img_h / self.height())
                real_w = int(w * img_w / self.width())
                real_h = int(h * img_h / self.height())
                self.roi_selected.emit(real_x, real_y, real_w, real_h)

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
