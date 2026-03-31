import cv2
import torch
from facenet_pytorch import MTCNN
import numpy as np

class FaceDetector:
    def __init__(self, device='cpu'):
        self.device = torch.device(device)
        self.mtcnn = MTCNN(keep_all=True, device=self.device)

    def detect(self, frame):
        """
        Detects faces in a frame.
        Returns: boxes (np.ndarray), probabilities (np.ndarray)
        """
        # Convert BGR (OpenCV) to RGB (MTCNN)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        boxes, probs = self.mtcnn.detect(frame_rgb)
        
        if boxes is None:
            return [], []
            
        return boxes, probs

    def get_face_crops(self, frame, boxes):
        """
        Crops faces from the frame based on bounding boxes.
        """
        faces = []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            # Ensure coordinates are within frame bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            face = frame[y1:y2, x1:x2]
            if face.size > 0:
                faces.append(face)
        return faces

if __name__ == "__main__":
    # Test Detector
    detector = FaceDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        boxes, probs = detector.detect(frame)
        
        for box, prob in zip(boxes, probs):
            if prob > 0.9:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{prob:.2f}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imshow("Detection Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
