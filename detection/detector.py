from ultralytics import YOLO
import cv2
import numpy as np

class PersonDetector:
    def __init__(self, model_name="yolov8n.pt", device='cpu'):
        self.model = YOLO(model_name)
        self.device = device

    def track_persons(self, frame, conf=0.5, persist=True):
        """
        Tracks persons in a frame.
        Returns: list of (track_id, box, confidence)
        """
        results = self.model.track(frame, conf=conf, persist=persist, classes=[0], device=self.device, verbose=False)
        
        tracking_result = []
        if results and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confs = results[0].boxes.conf.cpu().tolist()
            
            for tid, box, conf in zip(track_ids, boxes, confs):
                tracking_result.append((tid, box, conf))
                
        return tracking_result

    def annotate_frame(self, frame, detections, tracking=False):
        """
        Draws bounding boxes for detected/tracked persons.
        """
        for item in detections:
            if tracking:
                tid, box, conf = item
                label = f"ID: {tid} | {conf:.2f}"
            else:
                box, conf, cls = item
                label = f"Person {conf:.2f}"
                
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
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
