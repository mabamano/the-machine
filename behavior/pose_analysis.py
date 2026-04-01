import time
import numpy as np
from collections import deque

class PoseBehaviorDetector:
    def __init__(self, history_size=30, running_speed_threshold=50.0, fighting_variance_threshold=15.0):
        """
        history_size: Number of frames to keep for movement analysis.
        running_speed_threshold: Pixels per frame (normalized or raw) for running detection.
        fighting_variance_threshold: Variance in keypoint movement for fighting detection.
        """
        self.track_history = {} # {track_id: deque of {timestamp, keypoints, bbox, centroid}}
        self.history_size = history_size
        self.running_speed_threshold = running_speed_threshold
        self.fighting_variance_threshold = fighting_variance_threshold
        
        # Behavior states
        self.states = {} # {track_id: current_behavior}

    def update(self, tracking_data):
        """
        tracking_data: {track_id: {'bbox': [x1, y1, x2, y2], 'keypoints': [[x,y,conf], ...], 'centroid': [cx, cy]}}
        Returns lists of alerts.
        """
        current_time = time.time()
        alerts = []
        
        active_ids = list(tracking_data.keys())
        
        # Cleanup old tracks
        inactive_ids = set(self.track_history.keys()) - set(active_ids)
        for tid in inactive_ids:
            del self.track_history[tid]
            if tid in self.states:
                del self.states[tid]

        for tid, data in tracking_data.items():
            if tid not in self.track_history:
                self.track_history[tid] = deque(maxlen=self.history_size)
            
            self.track_history[tid].append({
                'time': current_time,
                'keypoints': data['keypoints'],
                'bbox': data['bbox'],
                'centroid': data['centroid']
            })
            
            # Analyze behavior for this track
            behavior = self._classify_behavior(tid)
            if behavior:
                self.states[tid] = behavior
                alerts.append({
                    "alert": f"{behavior} Detected",
                    "type": behavior,
                    "person_id": tid,
                    "timestamp": current_time
                })
        
        return alerts

    def _classify_behavior(self, tid):
        history = self.track_history[tid]
        if len(history) < 5:
            return None
        
        current = history[-1]
        
        # 1. "Fell Down" check (Horizontal orientation)
        x1, y1, x2, y2 = current['bbox']
        w, h = x2 - x1, y2 - y1
        is_horizontal = w > (h * 1.3)
        kpts = current['keypoints']
        if kpts is not None and len(kpts) > 12:
            head_y, l_hip_y, r_hip_y = kpts[0][1], kpts[11][1], kpts[12][1]
            if head_y > ((l_hip_y + r_hip_y)/2 - 10) and is_horizontal:
                 return "Fell Down"

        # 2. Velocity-based Analysis (Running/Fighting)
        recent = list(history)[-10:]
        total_centroid_dist = 0
        limb_motion_sum = 0
        
        for i in range(1, len(recent)):
            # Centroid speed
            c1, c2 = recent[i-1]['centroid'], recent[i]['centroid']
            total_centroid_dist += np.sqrt((c2[0]-c1[0])**2 + (c2[1]-c1[1])**2)
            
            # Limb speed (Wrist/Elbow movement)
            k1, k2 = recent[i-1]['keypoints'], recent[i]['keypoints']
            if k1 is not None and k2 is not None:
                # Track wrist/elbow 7,8,9,10
                for idx in [7, 8, 9, 10]:
                    limb_motion_sum += np.sqrt((k2[idx][0]-k1[idx][0])**2 + (k2[idx][1]-k1[idx][1])**2)

        avg_speed = total_centroid_dist / len(recent)
        avg_limb_speed = limb_motion_sum / (len(recent) * 4) # 4 joints tracked

        # Heuristic: Ratio of limb movement to body movement
        # During a run, limbs move fast but body also moves fast.
        # During a fight, limbs move MUCH faster than the body.
        limb_body_ratio = avg_limb_speed / (avg_speed + 0.1) # Avoid div by zero

        # FIGHTING: High limb movement AND high ratio (more arm motion than body travel)
        if avg_limb_speed > 25.0 and limb_body_ratio > 2.0:
            return "Fighting"
            
        # RUNNING: High body speed
        if avg_speed > self.running_speed_threshold:
            return "Running"
        
        # SLOWER FIGHTING: Low travel but high limb activity
        if avg_limb_speed > 15.0 and avg_speed < 10.0:
            return "Fighting"

        # 3. Loitering Analysis (Very low displacement)
        # ONLY if limb motion is ALSO low (to not confuse with fighting in place)
        c_start, c_end = history[0]['centroid'], history[-1]['centroid']
        displacement = np.sqrt((c_end[0]-c_start[0])**2 + (c_end[1]-c_start[1])**2)
        
        if displacement < 5.0 and avg_limb_speed < 5.0 and len(history) == self.history_size:
            return "Loitering"

        return None
