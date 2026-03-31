import time
import random
from .loitering import LoiteringDetector, ZoneViolationDetector

class BehaviorModule:
    def __init__(self, loitering_time=30.0, zone_rect=None):
        self.loitering_detector = LoiteringDetector(time_limit=loitering_time)
        self.zone_detector = ZoneViolationDetector(zone_rect=zone_rect)

    def analyze_behavior(self, tracking_data):
        """
        tracking_data: {track_id: {bbox: [x1, y1, x2, y2], centroid: [cx, cy]}}
        Returns: list of alerts.
        """
        tracked_ids = list(tracking_data.keys())
        
        # 1. Update loitering
        loitering_alerts = self.loitering_detector.update(tracked_ids)
        
        # 2. Update zone violations
        # Extract centroids for zone checks
        centroids = {tid: data['centroid'] for tid, data in tracking_data.items()}
        zone_alerts = self.zone_detector.update(centroids)
        
        return loitering_alerts + zone_alerts

def simulator():
    """
    Mock data sim for behavior analysis.
    """
    module = BehaviorModule(loitering_time=5.0, zone_rect=(50, 50, 150, 150))
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
