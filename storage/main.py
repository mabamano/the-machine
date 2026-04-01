import os
import sys
import numpy as np
from storage.database import StorageModule

def test_storage():
    """Standalone test for StorageModule functionality."""
    print("Testing StorageModule...")
    
    # Initialize module
    # Note: When running as 'python -m storage.main', 
    # the root directory must be in sys.path.
    storage = StorageModule(db_path="surveillance_history_test.db")
    
    # Mock data
    track_id = 42
    mock_embedding = np.random.rand(128).astype(np.float32)
    mock_frame_path = "recordings/test_frame_42.jpg"
    mock_confidence = 0.95
    
    # Test Insertion
    print(f"Inserting mock detection (ID: {track_id})...")
    storage.insert_detection(track_id, mock_embedding, mock_frame_path, mock_confidence)
    
    # Test Retrieval
    recent = storage.get_recent_detections(limit=1)
    if recent:
        print(f"Successfully retrieved latest detection: {recent[0][0]}, {recent[0][2]}, {recent[0][4]}, {recent[0][5]}")
        # Note: 0=id, 1=timestamp, 2=track_id, 3=embedding_blob, 4=frame_path, 5=confidence
    else:
        print("Error: No detections found in database.")
    
    # Test Pruning (Simulate 0h retention for testing)
    print("Testing Pruning (Temporarily setting retention to 0 hours)...")
    # Backup current config
    original_config_path = storage.config_path
    temp_config = "config_test.json"
    with open(temp_config, 'w') as f:
        import json
        json.dump({"RETENTION_HOURS": 0}, f)
        
    storage.config_path = temp_config # Redirect to temp config
    storage.prune_data()
    
    # Verify pruning
    after_prune = storage.get_recent_detections(limit=1)
    if not after_prune:
        print("Pruning successful: Database is empty.")
    else:
        print(f"Warning: Pruning failed, found {len(after_prune)} records.")
        
    # Clean up
    del storage # Ensure reference is gone and GC can close any lingering connections
    
    if os.path.exists(temp_config):
        os.remove(temp_config)
    
    try:
        if os.path.exists("surveillance_history_test.db"):
            os.remove("surveillance_history_test.db")
    except PermissionError as e:
        print(f"Warning: Could not delete test DB (locked by process). Clean up manually if needed. Error: {e}")
        
    print("StorageModule test complete.")

if __name__ == "__main__":
    test_storage()
