import sys
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtCore import QTimer
from .login import LoginWindow
from .main_window import MainWindow

class DashboardModule:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
            
        # Core Stack for Application States (Login <-> Dashboard)
        self.root_stack = QStackedWidget()
        self.root_stack.setWindowTitle("AI Smart Surveillance")
        self.root_stack.resize(1200, 800)
        
        self.login_win = LoginWindow()
        self.main_win = MainWindow()
        
        self.root_stack.addWidget(self.login_win)
        self.root_stack.addWidget(self.main_win)
        
        # Connect signals
        self.login_win.authenticated.connect(self._on_login_success)
        self.main_win.logout_requested.connect(self._on_logout)
        
        self.root_stack.setCurrentIndex(0) # Start with login

    def run(self):
        self.root_stack.show()
        return self.app.exec()

    def _on_login_success(self, success):
        if success:
            self.root_stack.setCurrentIndex(1)
            # Maybe initialize system stats here
            self.main_win.view_dashboard.update_stats(2, 45) # Mock stats

    def _on_logout(self):
        self.root_stack.setCurrentIndex(0)

    # Integration Hooks
    def update_display(self, frame, alerts=None):
        """
        Public API for the main integration to send frames and alerts.
        """
        # Pass to the dashboard overview
        self.main_win.view_dashboard.update_frame(frame)
        
        # Also pass to the camera management view if active (or just always for simplicity)
        self.main_win.view_cameras.player.update_frame(frame)

        if alerts:
            for alert in alerts:
                # Add to overview screen
                self.main_win.view_dashboard.add_alert(alert['type'], f"{alert['alert']} ({alert['person_id']})")
                
                # Capture a snapshot for the anomalies screen
                snapshot = frame.copy()
                # Add to anomalies screen with snapshot
                self.main_win.view_anomalies.add_anomaly_alert(
                    alert['type'], 
                    f"{alert['alert']} for {alert['person_id']}",
                    severity="High",
                    snapshot=snapshot
                )

if __name__ == "__main__":
    module = DashboardModule()
    
    # Standalone Test Simulation (NO WEBCAM)
    def simulate():
        # Consistent placeholder for mock mode
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, "DASHBOARD MOCK MODE", (150, 240), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 204), 2)
        module.update_display(frame)
        
    timer = QTimer()
    timer.timeout.connect(simulate)
    timer.start(33) # ~30 FPS
    
    module.run()
