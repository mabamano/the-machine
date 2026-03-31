import time
from collections import defaultdict

class LoiteringDetector:
    def __init__(self, time_limit=30.0):
        """
        time_limit: time in seconds to trigger loitering alert.
        """
        self.occupants = {}  # {person_id: entry_time}
        self.time_limit = time_limit
        self.alerts = []

    def update(self, tracked_ids):
        """
        tracked_ids: list of person IDs currently in the scene.
        """
        current_time = time.time()
        
        # New entrants
        for pid in tracked_ids:
            if pid not in self.occupants:
                self.occupants[pid] = current_time
                
        # Handle those who left (potential cleanup)
        to_remove = []
        for pid in self.occupants:
            if pid not in tracked_ids:
                # Need an "absent" counter to avoid jitter removal
                # For simplicity, we remove immediately
                to_remove.append(pid)
        for pid in to_remove:
            del self.occupants[pid]
            
        # Check for loitering
        alerts = []
        for pid, entry_time in self.occupants.items():
            duration = current_time - entry_time
            if duration > self.time_limit:
                alerts.append({
                    "alert": "Suspicious Activity",
                    "type": "Loitering",
                    "person_id": pid,
                    "duration": f"{duration:.1f}s"
                })
        return alerts

class ZoneViolationDetector:
    def __init__(self, zone_rect=None):
        """
        zone_rect: (x1, y1, x2, y2)
        """
        self.zone_rect = zone_rect

    def check_violation(self, person_coords):
        """
        person_coords: (x, y) - typically the bottom-center of bounding box.
        """
        if self.zone_rect is None:
            return False
            
        zx1, zy1, zx2, zy2 = self.zone_rect
        px, py = person_coords
        
        if zx1 <= px <= zx2 and zy1 <= py <= zy2:
            return True
        return False

    def update(self, tracked_objects):
        """
        tracked_objects: {person_id: (x, y)}
        """
        alerts = []
        for pid, (px, py) in tracked_objects.items():
            if self.check_violation((px, py)):
                alerts.append({
                    "alert": "Suspicious Activity",
                    "type": "Zone Violation",
                    "person_id": pid,
                    "location": f"({int(px)}, {int(py)})"
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
