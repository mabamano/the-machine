import os
import cv2
import numpy as np
from .detector import FaceDetector
from .embeddings import FaceNetModel
from .matcher import Matcher
from .database import EmbeddingDatabase

class FaceRecognitionModule:
    def __init__(self, db_path="embeddings.pkl", threshold=0.8, device='cpu'):
        self.detector = FaceDetector(device=device)
        self.model = FaceNetModel(device=device)
        self.matcher = Matcher(threshold=threshold)
        self.db = EmbeddingDatabase(storage_path=db_path)
        self.db.load()

    def recognize_faces(self, frame):
        """
        Detects and recognizes faces in a frame.
        Returns: [(name, confidence, box), ...]
        """
        boxes, probs = self.detector.detect(frame)
        results = []
        
        for box, prob in zip(boxes, probs):
            if prob > 0.9:  # Detection confidence
                x1, y1, x2, y2 = map(int, box)
                face_crop = frame[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    embedding = self.model.get_embedding(face_crop)
                    if embedding is not None:
                        name, confidence = self.matcher.find_best_match(embedding, self.db.get_all())
                        results.append((name, confidence, box))
                        
        return results

def test_module():
    """
    Stand-alone test/demo for the face recognition module.
    """
    module = FaceRecognitionModule()
    cap = cv2.VideoCapture(0)
    
    print("Starting Face Recognition Module Test. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        recognitions = module.recognize_faces(frame)
        
        for name, conf, box in recognitions:
            x1, y1, x2, y2 = map(int, box)
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{name} ({conf:.1f}%)", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        cv2.imshow("Face Recognition Module Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_module()
