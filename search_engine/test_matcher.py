import os
import sys
import time
import sqlite3
import pickle
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from search_engine.matcher import SearchMatcher

def setup_mock_db(db_path, num_records=1000):
    """
    Creates a mock surveillance_history.db with one match and N-1 random records.
    """
    if os.path.exists(db_path):
        os.remove(db_path)
        
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                track_id INTEGER,
                embedding BLOB,
                frame_path TEXT,
                confidence REAL
            )
        ''')
        
        # 1. Target embedding
        # Ensure it's a normalized embedding if the matcher expects it (though cosine handles it)
        target_emb = np.random.rand(512).astype(np.float32)
        target_emb /= np.linalg.norm(target_emb)
        target_blob = pickle.dumps(target_emb)
        
        # Insert the "True Match" with a very recent timestamp
        now_str = time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO detections (track_id, embedding, frame_path, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, target_blob, 'recordings/target_match.jpg', 0.99, now_str))
        
        # 2. Random embeddings
        # Batch insert for speed
        random_records = []
        for i in range(num_records - 1):
            random_emb = np.random.rand(512).astype(np.float32)
            random_emb /= np.linalg.norm(random_emb) # Good practice to normalize
            random_blob = pickle.dumps(random_emb)
            random_records.append((i + 2, random_blob, f'recordings/random_{i}.jpg', 0.5, now_str))
        
        cursor.executemany('''
            INSERT INTO detections (track_id, embedding, frame_path, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', random_records)
            
        conn.commit()
    return target_emb

def test_matcher_performance():
    db_path = "surveillance_history.db"
    num_test_records = 1000
    print(f"Setting up mock database with {num_test_records} records at {db_path}...")
    target_emb = setup_mock_db(db_path, num_test_records)
    
    # Mock FaceRecognitionModule to return our target_emb
    class MockFR:
        class MockModel:
            def get_embedding(self, face_crop): return target_emb
        class MockDetector:
            def detect(self, frame): return np.array([[0,0,10,10]]), np.array([0.99])
        def __init__(self):
            self.model = self.MockModel()
            self.detector = self.MockDetector()
            
    matcher = SearchMatcher(MockFR())
    
    # Create a dummy image for the search
    dummy_img_path = "dummy_query.jpg"
    cv2.imwrite(dummy_img_path, np.zeros((100, 100, 3), dtype=np.uint8))
    
    print(f"Searching 1,000 records...")
    start_time = time.time()
    
    try:
        with sqlite3.connect(db_path) as conn:
            results = matcher.search_for_target(dummy_img_path, conn)
    except Exception as e:
        print(f"Error during search: {e}")
        raise
        
    duration = time.time() - start_time
    print(f"\nTime taken to search {num_test_records} records: {duration:.4f}s")
    
    # Assertions
    assert len(results) > 0, "No results returned"
    assert results[0]['frame_path'] == 'recordings/target_match.jpg', f"Target match is not the top result! Top was {results[0]['frame_path']}"
    assert duration < 2.0, f"Search took too long: {duration:.4f}s (Target: < 2s)"
    
    print("Assertion Passed: Match is top result.")
    print(f"Assertion Passed: Duration {duration:.4f}s < 2.0s.")
    
    # Cleanup
    if os.path.exists(dummy_img_path):
        os.remove(dummy_img_path)
    # Keeping db_path as requested "Mock surveillance_history.db"

if __name__ == "__main__":
    try:
        test_matcher_performance()
        print("\nSuccess: Verification script completed successfully.")
    except AssertionError as ae:
        print(f"\nAssertion Failed: {ae}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
