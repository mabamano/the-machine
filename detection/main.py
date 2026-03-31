import cv2
import time
from .detector import PersonDetector

class DetectionModule:
    def __init__(self, model_name="yolov8n.pt", device='cpu'):
        self.detector = PersonDetector(model_name=model_name, device=device)

    def get_detected_frames(self, frame, conf=0.5):
        """
        Process a single frame and return tracking data.
        Returns: (annotated_frame, tracking_results)
        """
        track_results = self.detector.track_persons(frame, conf=conf)
        annotated_frame = self.detector.annotate_frame(frame.copy(), track_results, tracking=True)
        return annotated_frame, track_results

def test_module():
    """
    Stand-alone test/demo for the detection module.
    """
    module = DetectionModule()
    cap = cv2.VideoCapture(0)
    
    print("Starting Detection Module Test. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        annotated_frame, detections = module.get_detected_frames(frame)
            
        cv2.imshow("Detection Module Test", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_module()
