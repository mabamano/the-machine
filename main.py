import cv2
import sys
import time
from PySide6.QtCore import QTimer, Qt
from detection.main import DetectionModule
from face_recognition.main import FaceRecognitionModule
from behavior.main import BehaviorModule
from dashboard.main import DashboardModule

class SmartSurveillanceSystem:
    def __init__(self, camera_idx=0):
        # 1. Initialize Modules
        print("Initializing modules...")
        self.detection_mod = DetectionModule()
        self.recognition_mod = FaceRecognitionModule()
        self.behavior_mod = BehaviorModule(loitering_time=10.0, zone_rect=(50, 50, 400, 480))
        self.dashboard_mod = DashboardModule()
        
        # 2. Camera Setup
        self.cap = cv2.VideoCapture(camera_idx)
        if not self.cap.isOpened():
            print(f"Error: Camera {camera_idx} not found.")
            sys.exit(1)
            
        # 3. Processing Loop setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.fps_last_time = time.time()
        self.frame_count = 0

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
            
        # --- PHASE 1: Detection & Tracking ---
        # Get annotated frame (with boxes) and raw tracking data
        annotated_frame, tracking_results = self.detection_mod.get_detected_frames(frame)
        
        # --- PHASE 2: Face Recognition ---
        # We only run face recognition on the first person detected to save resources, 
        # or every N frames, or for all. Let's do all for now but check if any person is close.
        recognitions = []
        # Optimization: Only recognize if person is significant size
        for tid, box, conf in tracking_results:
            x1, y1, x2, y2 = map(int, box)
            # Annotate with recognition results if any
            # For simplicity, we just pass the frame to recognition mod
            pass
            
        # Run recognition on the whole frame (internally it detects faces again or we could pass crops)
        # To avoid double detection, we use the module's logic
        recognitions = self.recognition_mod.recognize_faces(frame)
        
        for name, conf, box in recognitions:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Face: {name}", (x1, y2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # --- PHASE 3: Behavior Analysis ---
        # Convert tracking results to format expected by behavior module
        # {track_id: {bbox: [x1, y1, x2, y2], centroid: [cx, cy]}}
        behavior_input = {}
        for tid, box, conf in tracking_results:
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            behavior_input[tid] = {"bbox": box, "centroid": [cx, cy]}
            
        alerts = self.behavior_mod.analyze_behavior(behavior_input)
        
        # --- PHASE 4: UI Update ---
        self.dashboard_mod.update_display(annotated_frame, alerts)
        
        # Calculate FPS
        self.frame_count += 1
        curr_time = time.time()
        if curr_time - self.fps_last_time >= 1.0:
            fps = self.frame_count / (curr_time - self.fps_last_time)
            # Update the dashboard stats through its main screen interface
            self.dashboard_mod.main_win.view_dashboard.update_stats(1, len(tracking_results))
            self.frame_count = 0
            self.fps_last_time = curr_time

    def start(self):
        print("System started.")
        self.timer.start(10) # ~100 FPS target (limited by processing)
        return self.dashboard_mod.run()

if __name__ == "__main__":
    system = SmartSurveillanceSystem()
    system.start()
