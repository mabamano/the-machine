import time
import random
from .loitering import LoiteringDetector, IntrusionDetector
from .action_analyzer import ActionAnalyzer

class BehaviorModule:
    def __init__(self, loitering_time=30.0, intrusion_roi=None):
        self.loitering_detector = LoiteringDetector(time_limit=loitering_time)
        self.intrusion_detector = IntrusionDetector(roi_rect=intrusion_roi)
        self.pose_detector = ActionAnalyzer()
        
        # Cooldown management: { (track_id, alert_type): last_time }
        self.last_alerts = {}
        self.cooldown = 10.0 # 10 seconds between same alerts

    def analyze_behavior(self, tracking_data):
        """
        tracking_data: {track_id: {bbox: [x1, y1, x2, y2], centroid: [cx, cy], keypoints: [[x,y,conf], ...]}}
        Returns: list of alerts.
        """
        current_time = time.time()
        raw_alerts = []
        
        # 1. Update loitering
        raw_alerts += self.loitering_detector.update(tracking_data)
        
        # 2. Update intrusions
        raw_alerts += self.intrusion_detector.update(tracking_data)
        
        # 3. Update Pose-based behaviors
        action_output = self.pose_detector.analyze_actions(tracking_data, current_time)
        for res in action_output.get("results", []):
            if res["action"] != "none":
                raw_alerts.append({
                    "alert": f"{res['action']} Detected",
                    "type": res["action"],
                    "person_id": res["track_id"],
                    "timestamp": current_time,
                    "confidence": res.get("confidence", 0.0)
                })
        
        # 4. Filter through Cooldown
        filtered_alerts = []
        for alert in raw_alerts:
            key = (alert['person_id'], alert['type'])
            if key not in self.last_alerts or (current_time - self.last_alerts[key] > self.cooldown):
                self.last_alerts[key] = current_time
                # Ensure 'alert' field exists for UI compatibility
                if 'alert' not in alert: alert['alert'] = f"{alert['type']} Detected"
                filtered_alerts.append(alert)
                
        return filtered_alerts

def simulator():
    """
    Mock data sim for behavior analysis.
    """
    module = BehaviorModule(loitering_time=5.0, intrusion_roi=(50, 50, 150, 150))
    print("Starting Behavior Module Simulator. Press Ctrl+C to stop.")
    
    # Simple simulated state
    try:
        t_start = time.time()
        while True:
            # Randomly simulate some movement
            p1_x = 100 + random.randint(-10, 10)
            p1_y = 100 + random.randint(-10, 10)
            
            # Simple data structure as expected by behavior analyzer
            tracking_data = {
                "P1": {"bbox": [p1_x-20, p1_y-40, p1_x+20, p1_y+40], "centroid": [p1_x, p1_y]}
            }
            
            alerts = module.analyze_behavior(tracking_data)
            for alert in alerts:
                print(f"[{time.strftime('%H:%M:%S')}] ALERT: {alert['type']} for {alert['person_id']}")
                
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Simulator stopped.")

if __name__ == "__main__":
    simulator()
