from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QSizePolicy, QMessageBox)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient, QBrush

class LoginWindow(QWidget):
    authenticated = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Surveillance System - Security Login")
        self.showMaximized() # Required by UI_Rules
        self.setStyleSheet("""
            QWidget { 
                background-color: #050505; 
                color: #fff; 
                font-family: 'Outfit', 'Inter', sans-serif; 
            }
            
            QFrame#LeftPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0088ff, stop:1 #002244);
                border-right: 1px solid #1a1a1a;
            }
            
            QFrame#RightPanel {
                background-color: #0d0d0d;
            }
            
            QLabel#BrandingTitle {
                font-size: 52px;
                font-weight: bold;
                color: #ffffff;
                letter-spacing: 1px;
            }
            
            QLabel#BrandingSubtitle {
                font-size: 20px;
                color: #88ccff;
                margin-top: 10px;
            }
            
            QLabel#LoginHeader {
                font-size: 32px;
                font-weight: bold;
                color: #0088ff;
                margin-bottom: 5px;
            }
            
            QLabel#LoginSub {
                font-size: 14px;
                color: #666;
                margin-bottom: 40px;
            }
            
            QLineEdit { 
                background-color: #1a1a1a; 
                border: 1px solid #333; 
                border-radius: 12px; 
                padding: 18px; 
                font-size: 16px; 
                color: #fff; 
                margin-bottom: 10px;
            }
            
            QLineEdit:focus { 
                border: 1px solid #0088ff; 
                background-color: #121212; 
            }
            
            QPushButton#LoginBtn { 
                background-color: #0088ff; 
                color: #fff; 
                font-weight: bold; 
                padding: 18px; 
                border-radius: 12px; 
                font-size: 18px; 
                margin-top: 15px;
                border: none;
            }
            
            QPushButton#LoginBtn:hover { 
                background-color: #0099ff; 
                border: 1px solid #44aaff;
            }
            
            QPushButton#LoginBtn:pressed { 
                background-color: #0066cc; 
            }
            
            QLabel#Footer {
                color: #444;
                font-size: 12px;
                margin-top: 50px;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # LEFT PANEL (Branding - 60%)
        self.left_panel = QFrame()
        self.left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Logo placeholder (can be an icon/image)
        self.logo_label = QLabel("🛡️")
        self.logo_label.setStyleSheet("font-size: 80px; margin-bottom: 20px;")
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        title = QLabel("AI SMART")
        title.setObjectName("BrandingTitle")
        title.setAlignment(Qt.AlignCenter)
        
        title2 = QLabel("SURVEILLANCE")
        title2.setObjectName("BrandingTitle")
        title2.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("High-Performance Security Monitoring")
        subtitle.setObjectName("BrandingSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(self.logo_label)
        left_layout.addWidget(title)
        left_layout.addWidget(title2)
        left_layout.addWidget(subtitle)
        
        # RIGHT PANEL (Login - 40%)
        self.right_panel = QFrame()
        self.right_panel.setObjectName("RightPanel")
        right_main_layout = QVBoxLayout(self.right_panel)
        right_main_layout.setAlignment(Qt.AlignCenter)
        
        # Centering widget for the form
        form_widget = QWidget()
        form_widget.setFixedWidth(400)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(10)
        
        login_header = QLabel("SECURE LOGIN")
        login_header.setObjectName("LoginHeader")
        login_header.setAlignment(Qt.AlignCenter)
        
        login_sub = QLabel("Enter your administrative credentials")
        login_sub.setObjectName("LoginSub")
        login_sub.setAlignment(Qt.AlignCenter)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setText("admin") # Pre-filled for development
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setText("admin") # Pre-filled for development
        
        self.btn_login = QPushButton("ACCESS SYSTEM")
        self.btn_login.setObjectName("LoginBtn")
        self.btn_login.clicked.connect(self._handle_login)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        
        footer = QLabel("© 2024 AI SECURITY SYSTEMS | ALL RIGHTS RESERVED")
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignCenter)
        
        form_layout.addWidget(login_header)
        form_layout.addWidget(login_sub)
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(self.pass_input)
        form_layout.addWidget(self.btn_login)
        form_layout.addWidget(footer)
        
        right_main_layout.addWidget(form_widget)
        
        main_layout.addWidget(self.left_panel, 6)
        main_layout.addWidget(self.right_panel, 4)

    def _handle_login(self):
        user = self.user_input.text().strip()
        pwd = self.pass_input.text().strip()
        
        if user == "admin" and pwd == "admin":
            print("Login successful")
            self.authenticated.emit(True)
        else:
            QMessageBox.warning(self, "Access Denied", "Invalid administrative credentials. Please try again.")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
