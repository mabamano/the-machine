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
        
        if boxes is None or len(boxes) == 0:
            return results
            
        for box, prob in zip(boxes, probs):
            if prob > 0.9:  # Detection confidence
                x1, y1, x2, y2 = map(int, box)
                # Bounds check
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
                face_crop = frame[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    embedding = self.model.get_embedding(face_crop)
                    if embedding is not None:
                        name, confidence = self.matcher.find_best_match(embedding, self.db.get_all())
                        results.append((name, confidence, box))
                        
        return results

    def add_target_person(self, name, image_path):
        """
        Dynamically adds a person from an image to the recognition database.
        """
        image = cv2.imread(image_path)
        if image is None: return False
        
        boxes, probs = self.detector.detect(image)
        if boxes is not None and len(boxes) > 0:
            box = boxes[0] # Use the best face detected
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            face_crop = image[y1:y2, x1:x2]
            
            if face_crop.size > 0:
                embedding = self.model.get_embedding(face_crop)
                if embedding is not None:
                    self.db.add_embedding(name, embedding)
                    self.db.save()
                    print(f"Dynamic Reg: {name} added to database.")
                    return True
        return False

def test_module(video_path=None):
    """
    Stand-alone test/demo for the face recognition module.
    """
    module = FaceRecognitionModule()
    
    if video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        # Placeholder Mode
        print("Testing with dummy frames (MOCK MODE).")
        cap = None
    
    while True:
        if cap:
            ret, frame = cap.read()
            if not ret: break
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "RECOGNITION DUMMY FEED", (150, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
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
