import cv2
import sys
import os
import time
import signal
import numpy as np
from PySide6.QtCore import QTimer, Qt, QThread, Signal, Slot, QObject
from detection.main import DetectionModule
from face_recognition.main import FaceRecognitionModule
from behavior.main import BehaviorModule
from dashboard.main import DashboardModule
from camera_storage import load_cameras

# Ensure Ctrl+C shuts down the app
signal.signal(signal.SIGINT, signal.SIG_DFL)

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
        self._running = True

    @Slot()
    def start_processing(self):
        # Timer MUST be created in the worker thread
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(33) # 33ms is ~30 FPS, MUCH better for GPU/CPU balance

    @Slot()
    def process_frame(self):
        if not self._running:
            if self.timer: self.timer.stop()
            return

        ret, frame = False, None
        
        if not self.placeholder_mode and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
        
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "STATUS: IDLE - NO FEED", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            cv2.putText(frame, "Please Select Camera in Sidebar", (160, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            self.frame_ready.emit(frame, [])
            return

        # Downsample
        h, w = frame.shape[:2]
        scale = 640.0 / w
        p_frame = cv2.resize(frame, (640, int(h * scale))) if scale < 1.0 else frame

        # AI Detection
        annotated_frame, tracking_results = self.detection_mod.get_detected_frames(p_frame)
        
        # Recognition (Every 15 frames)
        if self.frame_count % 15 == 0:
            try:
                recognitions = self.recognition_mod.recognize_faces(p_frame)
                for name, conf, face_box in recognitions:
                    fcx, fcy = (face_box[0]+face_box[2])/2, (face_box[1]+face_box[3])/2
                    for tid, box, tconf, kp in tracking_results:
                        # Match current face recognition to a tracking ID
                        if box[0] <= fcx <= box[2] and box[1] <= fcy <= box[3]:
                            self.person_recognitions[tid] = name
                            break
            except Exception:
                pass
        
        # Consistent Identity Assignment
        # Ensure that known names stay with the person even in frames where recognition didn't run
        for tid, box, conf, kp in tracking_results:
            if tid in self.person_recognitions:
                name = self.person_recognitions[tid]
                cv2.putText(annotated_frame, f"Face: {name}", 
                            (int(box[0]), int(box[1]) - 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # If we have a 'target' name, we could highlight it here
        
        # Behavior
        behavior_input = {t[0]: {"bbox": t[1], "centroid": [(t[1][0]+t[1][2])/2, (t[1][1]+t[1][3])/2], "keypoints": t[3]} 
                         for t in tracking_results}
        alerts = self.behavior_mod.analyze_behavior(behavior_input)
        
        self.frame_ready.emit(annotated_frame, alerts)
        self.frame_count += 1

    def stop(self):
        self._running = False
        if self.timer:
            self.timer.stop()

class SmartSurveillanceSystem(QObject):
    def __init__(self, video_path=None):
        super().__init__()
        print("Initializing AI Surveillance System (this may take a moment)...")
        # Initialize modules
        self.detection_mod = DetectionModule()
        self.recognition_mod = FaceRecognitionModule()
        self.behavior_mod = BehaviorModule(loitering_time=10.0)
        self.dashboard_mod = DashboardModule()
        
        self.dashboard_mod.main_win.view_cameras.camera_selected.connect(self.change_source)
        self.dashboard_mod.main_win.view_find.search_triggered.connect(self.on_search_triggered)
        
        # Threading Setup
        self.worker = VideoProcessor(self.detection_mod, self.recognition_mod, self.behavior_mod)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.frame_ready.connect(self.on_frame_ready, Qt.QueuedConnection)
        self.thread.started.connect(self.worker.start_processing)
        self.thread.start()

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

    @Slot(str)
    def on_search_triggered(self, image_path):
        # Extract name from image path or ask user (currently using filename)
        name = os.path.splitext(os.path.basename(image_path))[0]
        print(f"Adding new target for matching: {name}")
        self.recognition_mod.add_target_person(name, image_path)

    @Slot(object, list)
    def on_frame_ready(self, frame, alerts):
        self.dashboard_mod.update_display(frame, alerts)
        if self.worker.frame_count % 30 == 0:
            self.dashboard_mod.main_win.view_dashboard.update_stats(2, 0)

    def start(self):
        print("System ready. GUI running...")
        try:
            res = self.dashboard_mod.run()
        except KeyboardInterrupt:
            print("\nInterrupt received. Stopping system...")
            res = 0
            
        # Clean shutdown
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        print("System shutdown complete.")
        return res

if __name__ == "__main__":
    try:
        system = SmartSurveillanceSystem()
        EXIT_CODE = system.start()
        sys.exit(EXIT_CODE)
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected Fatal Error: {e}")
        sys.exit(1)
