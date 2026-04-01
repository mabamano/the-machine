import numpy as np
import pickle
import cv2
from datetime import datetime, timedelta

class SearchMatcher:
    def __init__(self, fr_module):
        """
        Initializes the SearchMatcher.
        :param fr_module: Instance of FaceRecognitionModule.
        """
        self.fr_module = fr_module

    def calculate_similarity(self, emb_blob, target_embedding):
        """
        Unpickles the DB BLOB to a numpy array and calculates Cosine Similarity.
        :param emb_blob: BLOB from SQLite database.
        :param target_embedding: Target float32 numpy array.
        :return: Cosine Similarity score.
        """
        try:
            stored_emb = pickle.loads(emb_blob)
            
            # Calculate Cosine Similarity
            dot_product = np.dot(target_embedding, stored_emb)
            norm_target = np.linalg.norm(target_embedding)
            norm_stored = np.linalg.norm(stored_emb)
            
            if norm_target == 0 or norm_stored == 0:
                return 0.0
                
            return float(dot_product / (norm_target * norm_stored))
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def search_for_target(self, image_path, db_conn):
        """
        Searches the database for the top 5 matches within the last 24 hours.
        :param image_path: Path to the target image.
        :param db_conn: SQLite database connection.
        :return: List of top 5 match dicts.
        """
        # Read the image
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Could not read image at {image_path}")

        # Detect face
        boxes, probs = self.fr_module.detector.detect(frame)
        if boxes is None or len(boxes) == 0:
            raise ValueError("No faces detected in the provided image.")

        # If multiple faces, pick the one with highest probability
        best_idx = np.argmax(probs)
        box = boxes[best_idx]
        x1, y1, x2, y2 = map(int, box)
        
        # Crop the face
        face_crop = frame[y1:y2, x1:x2]
        if face_crop.size == 0:
            raise ValueError("Invalid face crop.")

        # Generate embedding
        target_embedding = self.fr_module.model.get_embedding(face_crop)
        if target_embedding is None:
            raise ValueError("Could not generate embedding for the detected face.")

        # Query database for the last 24 hours
        cursor = db_conn.cursor()
        
        # SQLite datetime format 'YYYY-MM-DD HH:MM:SS'
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor.execute('''
                SELECT timestamp, frame_path, embedding, confidence 
                FROM detections 
                WHERE timestamp >= ?
            ''', (cutoff_str,))
            rows = cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Database query failed: {e}")

        # Process and calculate similarities
        results = []
        for row in rows:
            timestamp, frame_path, emb_blob, db_confidence = row
            similarity_score = self.calculate_similarity(emb_blob, target_embedding)
            
            results.append({
                'timestamp': timestamp,
                'frame_path': frame_path,
                'confidence_score': similarity_score, # Using similarity as confidence
                'db_confidence': db_confidence
            })

        # Sort descending based on similarity
        results.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        # Return top 5
        return results[:5]
