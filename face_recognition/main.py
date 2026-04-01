from .pipeline import get_pipeline, process_frame, process_query_image
from .database import get_db, add_new_person, load_faces, save_faces
import os
import cv2

class FaceRecognitionModule:
    def __init__(self, device='cpu'):
        # For compatibility with main.py
        self.pipeline = get_pipeline(device=device)

    def recognize_faces(self, frame):
        """
        Backward compatibility for main.py.
        Returns: [(name, confidence, box), ...]
        """
        results = self.pipeline.process_frame(frame)
        # Convert to expected format
        formatted = []
        for res in results:
            # We add person_id to the name to keep uniqueness visible as requested
            disp_name = f"{res['name']} ({res['person_id']})"
            formatted.append((disp_name, res['confidence'], res['box']))
        return formatted

    def add_target_person(self, name, image_path):
        """
        Explicitly registers a new person from an image.
        Uses add_new_person with a given name.
        """
        image = cv2.imread(image_path)
        if image is None: return False
        
        boxes, probs = self.pipeline.detector.detect(image)
        if len(boxes) > 0:
            box = boxes[0]
            x1, y1, x2, y2 = map(int, box)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            face_crop = image[y1:y2, x1:x2]
            
            if face_crop.size > 0:
                embedding = self.pipeline.model.get_embedding(face_crop)
                if embedding is not None:
                    # Clearer: If this was a query, it should match or be added.
                    # As requested: Add person manually via main.py
                    add_new_person(name, embedding)
                    return True
        return False

# Exporting pipeline functions for dashboard
from .pipeline import process_query_image as search_person
