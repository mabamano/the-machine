import cv2
import numpy as np
from .detector import FaceDetector
from .embeddings import FaceNetModel
from .database import load_faces, add_new_person, update_person_embedding, get_db
from .matcher import find_best_match

class FaceRecognitionPipeline:
    def __init__(self, device='cpu'):
        self.detector = FaceDetector(device=device)
        self.model = FaceNetModel(device=device)
        self.db = get_db()
        self.known_faces = self.db.load_faces()

    def process_query_image(self, image_path):
        """
        Processes an uploaded image to find a match in the database.
        Critical: Does NOT store the query image in the database.
        Required by USER_REQUEST.
        """
        image = cv2.imread(image_path)
        if image is None:
            return {"status": "error", "message": "Could not read image"}
            
        # 1. Detect face
        boxes, probs = self.detector.detect(image)
        if len(boxes) == 0:
            return {"status": "no_match", "message": "No face detected in query image"}
            
        # 2. Generate embedding for the best face
        box = boxes[0]
        x1, y1, x2, y2 = map(int, box)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
        face_crop = image[y1:y2, x1:x2]
        
        if face_crop.size == 0:
            return {"status": "error", "message": "Invalid crop"}
            
        embedding = self.model.get_embedding(face_crop)
        if embedding is None:
            return {"status": "error", "message": "Failed to generate embedding"}
            
        # 3. Compare against ALL stored embeddings
        # Step 3, 4, 5 of Matching_Pipeline
        person_id, name, score = find_best_match(embedding, self.known_faces)
        
        if person_id != "None":
            return {
                "status": "match",
                "person_id": person_id,
                "name": name,
                "confidence": score, # score is cosine similarity [0.6, 1.0]
                "message": "Match Found"
            }
        else:
            return {
                "status": "no_match",
                "message": "No Match Found",
                "confidence": score
            }

    def process_frame(self, frame):
        """
        Processes a video frame to detect and identify faces.
        Implements Identity_Assignment_Pipeline.
        Returns: list[dict]
        """
        # Reload known faces occasionally or use current db
        self.known_faces = self.db.faces
        
        boxes, probs = self.detector.detect(frame)
        results = []
        
        for box, prob in zip(boxes, probs):
            if prob < 0.9: continue
            
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            face_crop = frame[y1:y2, x1:x2]
            
            if face_crop.size == 0: continue
            
            embedding = self.model.get_embedding(face_crop)
            if embedding is None: continue
            
            # Step 3: Search in database
            person_id, name, score = find_best_match(embedding, self.known_faces)
            
            if person_id != "None":
                # IF match -> assign existing person_id + name
                # Optionally update person with new embedding for robustness
                if score < 0.85: # If it's a match but not perfect, add it for robustness
                    update_person_embedding(person_id, embedding)
                
                results.append({
                    "person_id": person_id,
                    "name": name,
                    "box": box,
                    "confidence": score
                })
            else:
                # Optimized: Do NOT auto-register Unknown for every frame.
                # Only return as unknown without persisting to database.
                results.append({
                    "person_id": "None",
                    "name": "Unknown",
                    "box": box,
                    "confidence": score
                })
                
        return results

# Global instances for use as requested
_pipeline_instance = None

def get_pipeline(device='cpu'):
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = FaceRecognitionPipeline(device=device)
    return _pipeline_instance

def process_query_image(image_path):
    return get_pipeline().process_query_image(image_path)

def process_frame(frame):
    return get_pipeline().process_frame(frame)
