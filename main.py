import cv2
import sys
import os
import time
import numpy as np
from PySide6.QtCore import QTimer, Qt
from PySide6.QtCore import QTimer, Qt, QThread, Signal, Slot, QObject
from detection.main import DetectionModule
from face_recognition.main import FaceRecognitionModule
from behavior.main import BehaviorModule
from dashboard.main import DashboardModule
from camera_storage import load_cameras

class VideoProcessor(QObject):
    frame_ready = Signal(object, list)

    def __init__(self, detection_mod, recognition_mod, behavior_mod):
        super().__init__()
        self.detection_mod = detection_mod
        self.recognition_mod = recognition_mod
        self.behavior_mod = behavior_mod
        self.frame_count = 0
        self.person_recognitions = {}
        self.cap = None
        self.placeholder_mode = True
        self.timer = None

    @Slot()
    def start_processing(self):
        # Timer MUST be created in the worker thread
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(1) # Run as fast as possible

    @Slot()
    def process_frame(self):
        ret, frame = False, None
        
        if not self.placeholder_mode and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
        
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "IDLE / SELECT SOURCE", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Downsample
        h, w = frame.shape[:2]
        scale = 640.0 / w
        p_frame = cv2.resize(frame, (640, int(h * scale))) if scale < 1.0 else frame

        # Detection
        annotated_frame, tracking_results = self.detection_mod.get_detected_frames(p_frame)
        
        # Recognition (Every 15 frames)
        if self.frame_count % 15 == 0:
            try:
                recognitions = self.recognition_mod.recognize_faces(p_frame)
                for name, conf, face_box in recognitions:
                    fcx, fcy = (face_box[0]+face_box[2])/2, (face_box[1]+face_box[3])/2
                    for tid, box, tconf, kp in tracking_results:
                        if box[0] <= fcx <= box[2] and box[1] <= fcy <= box[3]:
                            self.person_recognitions[tid] = name
                            break
            except: pass
        
        # Labels
        for tid, box, conf, kp in tracking_results:
            if tid in self.person_recognitions:
                cv2.putText(annotated_frame, f"Face: {self.person_recognitions[tid]}", 
                            (int(box[0]), int(box[1]) - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Behavior
        behavior_input = {t[0]: {"bbox": t[1], "centroid": [(t[1][0]+t[1][2])/2, (t[1][1]+t[1][3])/2], "keypoints": t[3]} 
                         for t in tracking_results}
        alerts = self.behavior_mod.analyze_behavior(behavior_input)
        
        self.frame_ready.emit(annotated_frame, alerts)
        self.frame_count += 1

class SmartSurveillanceSystem(QObject):
    def __init__(self, video_path=None):
        super().__init__()
        print("Initializing modules...")
        self.detection_mod = DetectionModule()
        self.recognition_mod = FaceRecognitionModule()
        self.behavior_mod = BehaviorModule(loitering_time=10.0)
        self.dashboard_mod = DashboardModule()
        
        self.dashboard_mod.main_win.view_cameras.camera_selected.connect(self.change_source)
        
        # Threading Setup
        self.worker = VideoProcessor(self.detection_mod, self.recognition_mod, self.behavior_mod)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.frame_ready.connect(self.on_frame_ready, Qt.QueuedConnection)
        self.thread.started.connect(self.worker.start_processing)
        self.thread.start() # Start the thread immediately

        if video_path: self.change_source(video_path)

    def change_source(self, path):
        if not os.path.exists(path): return
        
        # Update ROI globally
        cameras = load_cameras()
        new_roi = next((c.get('intrusion_roi') for c in cameras if c['video_path'] == path), None)
        self.behavior_mod.intrusion_detector.roi_rect = new_roi

        # Atomically switch the capture object in the worker
        old_cap = self.worker.cap
        new_cap = cv2.VideoCapture(path)
        
        if new_cap.isOpened():
            self.worker.cap = new_cap
            self.worker.placeholder_mode = False
            self.worker.person_recognitions = {}
            if old_cap: old_cap.release()
            print(f"Source change: {path}")
        else:
            self.worker.placeholder_mode = True

    @Slot(object, list)
    def on_frame_ready(self, frame, alerts):
        self.dashboard_mod.update_display(frame, alerts)
        if self.worker.frame_count % 30 == 0:
            self.dashboard_mod.main_win.view_dashboard.update_stats(2, 0)

    def start(self):
        print("System started.")
        res = self.dashboard_mod.run()
        # Clean shutdown
        self.thread.quit()
        self.thread.wait()
        return res

if __name__ == "__main__":
    system = SmartSurveillanceSystem()
    EXIT_CODE = system.start()
    sys.exit(EXIT_CODE)
