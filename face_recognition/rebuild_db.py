import os
import cv2
import numpy as np
from .detector import FaceDetector
from .embeddings import FaceNetModel
from .database import load_faces, save_faces, add_new_person, get_db

def rebuild(known_faces_dir="known_faces", device='cpu'):
    """
    Scans directory for images and generates embeddings in the JSON database format.
    """
    detector = FaceDetector(device=device)
    model = FaceNetModel(device=device)
    db = get_db()
    
    # Reset current database representation for clean rebuild? 
    # Or just append. Rebuild usually suggests clearing.
    db.faces = [] 
    
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
            if len(boxes) > 0:
                # Use best face
                box = boxes[0]
                x1, y1, x2, y2 = map(int, box)
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
                face_crop = image[y1:y2, x1:x2]
                
                if face_crop.size > 0:
                    embedding = model.get_embedding(face_crop)
                    if embedding is not None:
                        # Required: add_new_person(name: str, embedding: list) -> dict
                        add_new_person(name, embedding)
                        print(f"Registered identity: {name}")
                else:
                    print(f"Error cropping {filename}. Skipping.")
            else:
                print(f"No faces found in {filename}. Skipping.")
                
    db.save_faces()
    print("Database rebuilding (JSON) complete.")

if __name__ == "__main__":
    rebuild()
