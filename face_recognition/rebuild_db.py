import os
import cv2
import numpy as np
from .detector import FaceDetector
from .embeddings import FaceNetModel
from .database import EmbeddingDatabase

def rebuild(known_faces_dir="known_faces", db_path="embeddings.pkl", device='cpu'):
    """
    Scans directory for images and generates FaceNet embeddings.
    """
    detector = FaceDetector(device=device)
    model = FaceNetModel(device=device)
    db = EmbeddingDatabase(storage_path=db_path)
    
    if not os.path.exists(known_faces_dir):
        os.makedirs(known_faces_dir)
        print(f"Directory {known_faces_dir} created.")
        return

    print(f"Scanning {known_faces_dir} for images...")
    for filename in os.listdir(known_faces_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.splitext(filename)[0]
            img_path = os.path.join(known_faces_dir, filename)
            
            image = cv2.imread(img_path)
            if image is None:
                print(f"Skipping {filename}: Unable to read.")
                continue
                
            # Use detector to find face for cropping
            boxes, probs = detector.detect(image)
            if boxes is not None and len(boxes) > 0:
                # Use best face
                box = boxes[0]
                x1, y1, x2, y2 = map(int, box)
                face_crop = image[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    embedding = model.get_embedding(face_crop)
                    if embedding is not None:
                        db.add_embedding(name, embedding)
                        print(f"Added embedding for: {name}")
                else:
                    print(f"Error cropping {filename}. Skipping.")
            else:
                print(f"No faces found in {filename}. Skipping.")
                
    db.save()
    print("Database rebuilding complete.")

if __name__ == "__main__":
    rebuild()
