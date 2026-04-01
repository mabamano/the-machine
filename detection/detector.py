from ultralytics import YOLO
import cv2
import numpy as np

class PersonDetector:
    def __init__(self, model_name="yolov8n-pose.pt", device='cpu'):
        self.model = YOLO(model_name)
        self.device = device

    def track_persons(self, frame, conf=0.5, persist=True):
        """
        Tracks persons in a frame.
        Returns: list of (track_id, box, confidence, keypoints)
        """
        results = self.model.track(frame, conf=conf, persist=persist, classes=[0], device=self.device, verbose=False)
        
        tracking_result = []
        if results and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confs = results[0].boxes.conf.cpu().tolist()
            # YOLOv8 Pose results have .keypoints. Safely check if they exist.
            has_kpts = results[0].keypoints is not None
            if has_kpts:
                kpts = results[0].keypoints.data.cpu().numpy() # [num_objs, 17, 3]
            else:
                kpts = [None] * len(track_ids)
            
            for tid, box, conf, kp in zip(track_ids, boxes, confs, kpts):
                tracking_result.append((tid, box, conf, kp))
                
        return tracking_result

    def annotate_frame(self, frame, detections, tracking=False):
        """
        Draws bounding boxes and skeletons (if keypoints present) for detected/tracked persons.
        """
        # YOLOv8 Pose Connections (Skeletons)
        connections = [
            (0, 1), (0, 2), (1, 3), (2, 4), # Head
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10), # Upper Body
            (5, 11), (6, 12), (11, 12), # Torso
            (11, 13), (13, 15), (12, 14), (14, 16) # Lower Body
        ]
        
        for item in detections:
            if tracking:
                tid, box, conf, kp = item
                label = f"ID: {tid}"
            else:
                box, conf, cls = item
                label = f"Person {conf:.2f}"
                kp = None
                
            x1, y1, x2, y2 = map(int, box)
            color = (0, 255, 0) # Green for active tracking
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Skeleton (keypoints & connections)
            if kp is not None:
                try:
                    # Draw points
                    for k in kp:
                        kx, ky, kconf = k
                        if kconf > 0.5:
                            cv2.circle(frame, (int(kx), int(ky)), 2, (0, 0, 255), -1)
                    
                    # Draw connections
                    for start_idx, end_idx in connections:
                        sk, ek = kp[start_idx], kp[end_idx]
                        if sk[2] > 0.5 and ek[2] > 0.5:
                            cv2.line(frame, (int(sk[0]), int(sk[1])), (int(ek[0]), int(ek[1])), (255, 255, 0), 1)
                except:
                    pass
                        
        return frame

if __name__ == "__main__":
    # Test Detector
    detector = PersonDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        detections = detector.detect_persons(frame)
        detector.annotate_frame(frame, detections)
        
        cv2.imshow("Person Detection Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
