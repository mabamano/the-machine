import numpy as np
from .tracker_buffer import TrackerBuffer
from .utils import euclidean_distance, compute_iou

class ActionAnalyzer:
    def __init__(self, buffer_maxlen=30, frame_w=640, frame_h=480):
        self.tracker = TrackerBuffer(maxlen=buffer_maxlen)
        self.frame_w = frame_w
        self.frame_h = frame_h
        
        # Thresholds translated from user requirements (Tuned for normalized 640px width)
        self.velocity_threshold = 0.005
        self.iou_threshold = 0.1
        self.wrist_velocity_threshold = 0.02
        self.acceleration_threshold = 0.01
        self.fall_aspect_ratio_threshold = 1.3
        self.fall_height_drop_threshold = 0.15

    def analyze_actions(self, frame_data, current_time):
        """
        frame_data: {track_id: {bbox: [x1,y1,x2,y2], centroid: [cx,cy], keypoints: [[x,y,c]...]}}
        Returns an array of JSON objects per frame format.
        """
        current_ids = list(frame_data.keys())
        
        # Update buffer
        for tid, data in frame_data.items():
            kpts = data.get('keypoints')
            bbox = data.get('bbox')
            self.tracker.update_buffer(tid, kpts, bbox, self.frame_w, self.frame_h)
            
        self.tracker.cleanup(current_ids)
        
        results = []
        
        # Evaluate actions for each individual
        running_candidates = []
        fall_candidates = []
        
        for tid in current_ids:
            buf = self.tracker.get_buffer(tid)
            if self.detect_fall(buf):
                fall_candidates.append(tid)
            elif self.detect_running(buf):
                running_candidates.append(tid)

        # Evaluate fighting (pairwise)
        fighting_candidates = set()
        for i in range(len(current_ids)):
            for j in range(i+1, len(current_ids)):
                tid_a = current_ids[i]
                tid_b = current_ids[j]
                buf_a = self.tracker.get_buffer(tid_a)
                buf_b = self.tracker.get_buffer(tid_b)
                if self.detect_fighting(buf_a, buf_b):
                    fighting_candidates.add(tid_a)
                    fighting_candidates.add(tid_b)

        # Prepare results
        for tid in current_ids:
            action = "none"
            # Priority: Fighting > Fall > Running
            # Note: A fallen person in a fight might still be an alert
            if tid in fighting_candidates:
                action = "Fighting"
            elif tid in fall_candidates:
                action = "Fall"
            elif tid in running_candidates:
                action = "Running"
            
            if action != "none":
                results.append({
                    "track_id": tid,
                    "action": action,
                    "confidence": 0.85 if action == "Fall" else 0.8
                })
                
        # Return properly wrapped format according to JSON output contract
        return {
            "timestamp": current_time,
            "results": results
        }

    def detect_fall(self, buffer):
        """
        Detects falls based on aspect ratio, vertical velocity, and head-to-hip relation.
        """
        if not buffer or len(buffer) < 5:
            return False
            
        latest = buffer[-1]
        kpts = latest.get('keypoints')
        bbox = latest.get('bbox') # [x1, y1, x2, y2]
        
        if bbox is None or kpts is None or len(kpts) < 17:
            return False
            
        # 1. Aspect Ratio (Horizontal person)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        aspect_ratio = w / (h + 1e-6)
        is_horizontal = aspect_ratio > self.fall_aspect_ratio_threshold
        
        # 2. Vertical Drop (Normalized coordinates: 0 is top, 1 is bottom)
        # Check current nose (0) vs some frames back
        prev = buffer[-5] if len(buffer) >= 5 else buffer[0]
        kpts_prev = prev.get('keypoints')
        
        if kpts_prev is not None and len(kpts_prev) > 0:
            nose_curr = kpts[0][1]
            nose_prev = kpts_prev[0][1]
            drop = nose_curr - nose_prev
            
            # Rapid downward movement (positive change in Y)
            is_dropping = drop > 0.1 # Dropped 10% of frame height within 5 frames
            
            # 3. Head Position Relative to Hips
            # In a fall, the head (0) is usually below or at same height as hips (11, 12)
            hip_y = (kpts[11][1] + kpts[12][1]) / 2.0
            is_head_low = nose_curr > (hip_y - 0.05) # Head is not significantly above hips
            
            # Trigger if horizontal + head low, OR rapid drop + horizontal
            if (is_horizontal and is_head_low) or (is_dropping and is_horizontal):
                return True
                
        return False

    def detect_running(self, buffer):
        if not buffer or len(buffer) < 5:
            return False
            
        # 1. Centroid velocity (mean horizontal velocity > threshold)
        centroids = [f['centroid'] for f in buffer]
        dist_x = 0.0
        for i in range(1, len(centroids)):
            # horizontal velocity difference
            dist_x += abs(centroids[i][0] - centroids[i-1][0])
            
        avg_speed_x = dist_x / len(centroids)
        
        # 2. Periodic oscillation in ankle distance (indicates legs moving)
        ankles_dists = []
        for f in buffer:
            kpts = f['keypoints']
            if kpts is not None and len(kpts) > 16:
                a1, a2 = kpts[15], kpts[16] # Left ankle, Right ankle
                if a1[2] > 0.3 and a2[2] > 0.3:
                    ankles_dists.append(euclidean_distance(a1[:2], a2[:2]))
            
        var = np.var(ankles_dists) if len(ankles_dists) > 2 else 0.0
        
        return avg_speed_x > self.velocity_threshold and var > 0.00005

    def detect_fighting(self, buf_a, buf_b):
        if not buf_a or not buf_b or len(buf_a) < 3 or len(buf_b) < 3:
            return False
            
        latest_a = buf_a[-1]
        latest_b = buf_b[-1]
        
        # Condition 1: IoU > threshold
        iou = compute_iou(latest_a['bbox'], latest_b['bbox'])
        if iou < self.iou_threshold:
            return False
            
        # Check striking conditions (wrist rapidly moving)
        return self._check_striking(buf_a) or self._check_striking(buf_b)

    def _check_striking(self, attacker_buf):
        # Wrist indices: 9, 10
        latest = attacker_buf[-1]
        prev = attacker_buf[-2]
        
        kpts_lat = latest['keypoints']
        kpts_prev = prev['keypoints']
        
        if kpts_lat is None or kpts_prev is None or len(kpts_lat) <= 10:
            return False
            
        w9_lat, w9_prev = kpts_lat[9], kpts_prev[9]
        w10_lat, w10_prev = kpts_lat[10], kpts_prev[10]
        
        s9 = euclidean_distance(w9_prev[:2], w9_lat[:2]) if w9_lat[2] > 0.3 and w9_prev[2] > 0.3 else 0.0
        s10 = euclidean_distance(w10_prev[:2], w10_lat[:2]) if w10_lat[2] > 0.3 and w10_prev[2] > 0.3 else 0.0
        
        accel = 0.0
        if len(attacker_buf) >= 3:
            p2 = attacker_buf[-3]['keypoints']
            if p2 is not None and len(p2) > 10:
                s1_9 = euclidean_distance(p2[9][:2], w9_prev[:2]) if p2[9][2] > 0.3 and w9_prev[2] > 0.3 else 0.0
                s1_10 = euclidean_distance(p2[10][:2], w10_prev[:2]) if p2[10][2] > 0.3 and w10_prev[2] > 0.3 else 0.0
                accel = max(accel, s9 - s1_9, s10 - s1_10)
        
        if (s9 > self.wrist_velocity_threshold or s10 > self.wrist_velocity_threshold) and accel > self.acceleration_threshold:
            return True
            
        return False
