import time
from collections import defaultdict

class LoiteringDetector:
    def __init__(self, time_limit=30.0):
        self.occupants = {}  # {person_id: {'entry_time': t, 'last_pos': (x,y), 'still_start': t}}
        self.time_limit = time_limit

    def update(self, tracking_data):
        current_time = time.time()
        alerts = []
        
        # Track IDs in current frame
        current_ids = list(tracking_data.keys())
        
        # 1. Update occupants
        for pid in current_ids:
            pos = tracking_data[pid]['centroid']
            if pid not in self.occupants:
                self.occupants[pid] = {'entry_time': current_time, 'last_pos': pos, 'still_start': current_time}
            else:
                # Check if moved
                prev_pos = self.occupants[pid]['last_pos']
                dist = ((pos[0]-prev_pos[0])**2 + (pos[1]-prev_pos[1])**2)**0.5
                if dist > 5.0: # Significant movement
                    self.occupants[pid]['still_start'] = current_time
                    self.occupants[pid]['last_pos'] = pos
                
                # Check duration of being "still"
                still_duration = current_time - self.occupants[pid]['still_start']
                if still_duration > self.time_limit:
                    alerts.append({
                        "alert": "Loitering Detected",
                        "type": "Loitering",
                        "person_id": pid,
                        "details": f"Stationary for {still_duration:.1f}s"
                    })
                    
        # Cleanup
        to_remove = [pid for pid in self.occupants if pid not in current_ids]
        for pid in to_remove:
            del self.occupants[pid]
            
        return alerts

class IntrusionDetector:
    def __init__(self, roi_rect=None):
        """
        roi_rect: (x1, y1, x2, y2)
        """
        self.roi_rect = roi_rect

    def update(self, tracking_data):
        if not self.roi_rect:
            return []
            
        alerts = []
        rx1, ry1, rx2, ry2 = self.roi_rect
        for pid, data in tracking_data.items():
            px, py = data['centroid']
            if rx1 <= px <= rx2 and ry1 <= py <= ry2:
                alerts.append({
                    "alert": "Restricted Area Access",
                    "type": "Intrusion",
                    "person_id": pid,
                    "details": f"In ROI at ({int(px)}, {int(py)})"
                })
        return alerts

if __name__ == "__main__":
    # Test Behavioral detectors
    ld = LoiteringDetector(time_limit=2.0)
    zd = ZoneViolationDetector(zone_rect=(10, 10, 100, 100))
    
    print("Simulated test...")
    # T=0
    print(f"T=0: Alerts: {ld.update(['p1'])}")
    time.sleep(1)
    # T=1
    print(f"T=1: Alerts: {ld.update(['p1'])}")
    time.sleep(1.5)
    # T=2.5 - Loitering alert expected
    print(f"T=2.5: Alerts: {ld.update(['p1'])}")
    
    # Zone violation
    print(f"Zone test: {zd.update({'p2': (50, 50)})}")
    print(f"Zone test: {zd.update({'p3': (200, 50)})}")
