import time
from collections import deque
from .utils import normalize_keypoints, compute_centroid

class TrackerBuffer:
    def __init__(self, maxlen=30):
        self.buffer = {}
        self.maxlen = maxlen
        
    def update_buffer(self, track_id, keypoints, bbox, frame_w, frame_h):
        if track_id not in self.buffer:
            self.buffer[track_id] = deque(maxlen=self.maxlen)
            
        norm_kpts = normalize_keypoints(keypoints, frame_w, frame_h)
        centroid = compute_centroid(bbox)
        # We store normalized centroid for displacement calculations
        norm_centroid = [centroid[0] / frame_w if frame_w else 0.0, 
                         centroid[1] / frame_h if frame_h else 0.0]
        
        self.buffer[track_id].append({
            'timestamp': time.time(),
            'keypoints': norm_kpts,
            'bbox': bbox,
            'centroid': norm_centroid
        })
        
    def get_buffer(self, track_id):
        return self.buffer.get(track_id, None)

    def cleanup(self, current_ids):
        to_remove = [tid for tid in self.buffer if tid not in current_ids]
        for tid in to_remove:
            del self.buffer[tid]
