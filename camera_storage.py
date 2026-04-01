import json
import os
import uuid

DATA_DIR = "data"
CAMERAS_FILE = os.path.join(DATA_DIR, "cameras.json")

def initialize_storage():
    """Ensure data directory and cameras.json exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(CAMERAS_FILE):
        with open(CAMERAS_FILE, 'w') as f:
            json.dump([], f)

def load_cameras():
    """Load all cameras from JSON file."""
    initialize_storage()
    try:
        with open(CAMERAS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_cameras(cameras):
    """Save the full camera list to JSON file."""
    initialize_storage()
    with open(CAMERAS_FILE, 'w') as f:
        json.dump(cameras, f, indent=4)

def add_camera(camera_dict):
    """
    Validates and adds a new camera to storage.
    camera_dict should have 'name' and 'video_path'.
    """
    # Validation
    if not os.path.exists(camera_dict.get('video_path', '')):
        raise FileNotFoundError(f"Video path does not exist: {camera_dict.get('video_path')}")
        
    cameras = load_cameras()
    
    # Check for duplicates by path (optional but good)
    for cam in cameras:
        if cam['video_path'] == camera_dict['video_path']:
             # Already exists, we can update or skip. Let's just update the name.
             cam['name'] = camera_dict['name']
             save_cameras(cameras)
             return cam
             
    # Generate ID if missing
    if 'camera_id' not in camera_dict:
        camera_dict['camera_id'] = f"cam_{len(cameras) + 1:03d}_{uuid.uuid4().hex[:4]}"
    
    if 'status' not in camera_dict:
        camera_dict['status'] = "active"
        
    cameras.append(camera_dict)
    save_cameras(cameras)
    return camera_dict

def delete_camera(camera_id):
    """Remove a camera from storage by its ID."""
    cameras = load_cameras()
    updated = [c for c in cameras if c.get('camera_id') != camera_id]
    save_cameras(updated)
    return len(cameras) != len(updated)

def update_camera(camera_id, updated_fields):
    """
    Apply any changes to an existing camera by its ID.
    Example updated_fields: {'name': 'New Entrance', 'video_path': 'C:/v2.mp4'}
    """
    cameras = load_cameras()
    found = False
    for cam in cameras:
        if cam.get('camera_id') == camera_id:
            cam.update(updated_fields)
            found = True
            break
            
    if found:
        save_cameras(cameras)
    return found

if __name__ == "__main__":
    # Test logic
    initialize_storage()
    print("Storage initialized.")
    cameras = load_cameras()
    print(f"Loaded {len(cameras)} cameras.")
