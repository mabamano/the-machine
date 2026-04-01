import cv2
import time
from .detector import PersonDetector

class DetectionModule:
    def __init__(self, model_name="yolov8n-pose.pt", device='cpu'):
        self.detector = PersonDetector(model_name=model_name, device=device)

    def get_detected_frames(self, frame, conf=0.5):
        """
        Process a single frame and return tracking data.
        Returns: (annotated_frame, tracking_results)
        """
        track_results = self.detector.track_persons(frame, conf=conf)
        annotated_frame = self.detector.annotate_frame(frame.copy(), track_results, tracking=True)
        return annotated_frame, track_results

def test_module(video_path=None):
    """
    Stand-alone test/demo for the detection module.
    """
    module = DetectionModule()
    
    if video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        # Placeholder/DUMMY Mode
        print("Testing with dummy frames (MOCK MODE).")
        cap = None
    
    while True:
        if cap:
            ret, frame = cap.read()
            if not ret: break
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "DETECTION DUMMY FEED", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        annotated_frame, detections = module.get_detected_frames(frame)
            
        cv2.imshow("Detection Module Test", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_module()
